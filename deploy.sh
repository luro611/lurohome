#!/bin/zsh
# Baut die Website lurohome.de und lädt dist/ zu ALL-INKL hoch.
#   ./deploy.sh          Probelauf: baut und zeigt nur, was übertragen würde
#   ./deploy.sh --jetzt  wirklich hochladen, danach live prüfen, Tag web-<Version> setzen und pushen
# Regeln: CLAUDE.md. --jetzt nur nach Probelauf und Freigabe durch Lutz.

NAME="lurohome"
DOMAIN="lurohome.de"
BUILD="python3 src/build.py"
SPERRE=""

# ---------------------------------------------------------------------------
# Ab hier ist das Skript bei allen drei Seiten gleich (rothe-it, lurohome, lenkwerk-eu).
# Zugang (nicht im Repository): .env neben diesem Skript, Vorlage .env.beispiel.
#   ZUGANG=ssh   rsync über SSH, Host-Eintrag in ~/.ssh/config (SSH_HOST), Zielordner ZIEL
#   ZUGANG=ftps  lftp über FTPS, FTP_HOST und FTP_USER, Passwort im macOS-Schlüsselbund (Dienst web-ftp-<Domain>)
# Kein Löschen auf dem Server: Dateien, die nicht aus dist/ kommen, bleiben stehen.
set -euo pipefail
cd "$(dirname "$0")"

fehler() { echo "Abbruch: $*" >&2; exit 1; }
JETZT=0
case "${1:-}" in
  --jetzt) JETZT=1 ;;
  "") ;;
  *) echo "Aufruf: ./deploy.sh (Probelauf) oder ./deploy.sh --jetzt (hochladen)"; exit 2 ;;
esac

ZUGANG="" SSH_HOST="" ZIEL="" FTP_HOST="" FTP_USER=""
[[ -f .env ]] && source ./.env
[[ -n "$ZUGANG" ]] || fehler "In .env fehlt ZUGANG (ssh oder ftps). Vorlage: .env.beispiel"

# Sperre (nur lenkwerk.eu): Hochladen erst nach ausdrücklicher Freigabe
if (( JETZT )) && [[ -n "${SPERRE:-}" ]]; then
  eval "$SPERRE" || fehler "$SPERRE_TEXT"
fi

# Echte Uploads nur von einem committeten Stand, damit das Tag stimmt
if (( JETZT )) && [[ -n "$(git status --porcelain -- src logos 2>/dev/null)" ]]; then
  fehler "Änderungen in src/ sind nicht committet. Erst committen, dann hochladen."
fi

echo "== Bauen: $BUILD"
eval "$BUILD"

VERSION=$(grep -oE 'Version 20[0-9]{2}\.[0-9]{2}\.[0-9]{2}(-[0-9]+)?' dist/index.html | head -1 | cut -d' ' -f2 || true)
[[ -n "$VERSION" ]] || fehler "Keine Version in dist/index.html gefunden."
echo "== Version $VERSION, Ziel $DOMAIN, Zugang $ZUGANG"

case "$ZUGANG" in
  ssh)
    [[ -n "$SSH_HOST" ]] || fehler "In .env fehlt SSH_HOST (Name aus ~/.ssh/config)."
    [[ -n "$ZIEL" ]] || fehler "In .env fehlt ZIEL (Ordner der Domain auf dem Server, z. B. ${DOMAIN}/)."
    command -v rsync >/dev/null || fehler "rsync fehlt (brew install rsync)."
    OPTS=(-rlvz --checksum --itemize-changes --chmod=D755,F644 --exclude=.DS_Store --exclude="*-website-*.zip")
    (( JETZT )) || OPTS+=(--dry-run)
    rsync "${OPTS[@]}" dist/ "$SSH_HOST:$ZIEL"
    ;;
  ftps)
    [[ -n "$FTP_HOST" ]] || fehler "In .env fehlt FTP_HOST (z. B. w0123456.kasserver.com)."
    command -v lftp >/dev/null || fehler "lftp fehlt (brew install lftp)."
    [[ -n "$FTP_USER" ]] || fehler "In .env fehlt FTP_USER (FTP-Benutzer dieser Domain)."
    # Passwort aus dem macOS-Schlüsselbund (Lutz legt es einmal an), nie in Dateien oder auf der Kommandozeile
    DIENST="${FTP_DIENST:-web-ftp-$DOMAIN}"
    LFTP_PASSWORD=$(security find-generic-password -a "$FTP_USER" -s "$DIENST" -w 2>/dev/null) || \
      fehler "Kein Passwort im Schlüsselbund (Dienst $DIENST, Konto $FTP_USER). Lutz legt es an mit:
  security add-generic-password -U -a $FTP_USER -s $DIENST -w"
    export LFTP_PASSWORD
    # Der FTP-Benutzer der Domain sieht nur ihren Ordner, darum ist das Ziel dort "/"
    MOPTS="--reverse --overwrite --verbose --exclude-glob .DS_Store --exclude-glob *-website-*.zip"
    (( JETZT )) || MOPTS+=" --dry-run"
    lftp -c "set ftp:ssl-force true; set ftp:ssl-protect-data true; set ssl:verify-certificate true; set net:max-retries 2; set cmd:fail-exit true; open --user $FTP_USER --env-password ftp://$FTP_HOST; mirror $MOPTS dist/ ${ZIEL:-/}"
    unset LFTP_PASSWORD
    ;;
  *) fehler "ZUGANG muss ssh oder ftps sein, nicht \"$ZUGANG\"." ;;
esac

if (( ! JETZT )); then
  echo "== Probelauf, nichts übertragen. Hochladen (nach Freigabe durch Lutz): ./deploy.sh --jetzt"
  exit 0
fi

echo "== Live prüfen: https://$DOMAIN/"
ONLINE=$(curl -fsS -H 'Cache-Control: no-cache' "https://$DOMAIN/?v=$VERSION" | grep -oE 'Version 20[0-9.]+(-[0-9]+)?' | head -1 | cut -d' ' -f2 || true)
if [[ "$ONLINE" != "$VERSION" ]]; then
  fehler "Online steht Version \"${ONLINE:-keine}\", erwartet $VERSION. Kein Tag gesetzt; bitte nachsehen."
fi
echo "   online: Version $ONLINE"

TAG="web-$VERSION"
if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "== Tag $TAG gibt es schon."
else
  git tag -a "$TAG" -m "$NAME $VERSION"
  echo "== Tag $TAG gesetzt."
fi
git push origin "$(git branch --show-current)" "$TAG"   # Commit und Tag auf GitHub
echo "== Fertig: https://$DOMAIN/ hat Version $VERSION ($TAG)."
