#!/bin/zsh
# Holt das neueste Lichtkammer-Testpaket aus dem Lichtkammer-Ordner nach extras/lichtkammer-download/.
#   extras/lichtkammer-paket-holen.sh [Pfad/zu/lichtkammer/dist]
# Danach: python3 src/build.py, ./deploy.sh (Probelauf). Siehe extras/lichtkammer-download/README.md
set -euo pipefail
setopt null_glob
cd "$(dirname "$0")/.."
QUELLE="${1:-../../lichtkammer/dist}"
ZIEL="extras/lichtkammer-download"
[[ -d "$QUELLE" ]] || { echo "Abbruch: $QUELLE gibt es nicht (Pfad zu lichtkammer/dist als Argument angeben)." >&2; exit 1; }

ZIP=$(ls "$QUELLE"/lichtkammer-testpaket-*.zip 2>/dev/null | sort -V | tail -1 || true)
[[ -n "$ZIP" ]] || { echo "Abbruch: In $QUELLE liegt kein lichtkammer-testpaket-*.zip." >&2; exit 1; }
NAME=$(basename "$ZIP")
[[ -f "$ZIP.sha256" ]] || { echo "Abbruch: $NAME.sha256 fehlt." >&2; exit 1; }

# Prüfsumme gegenprüfen, bevor etwas kopiert wird
SOLL=$(cut -d' ' -f1 "$ZIP.sha256"); IST=$(shasum -a 256 "$ZIP" | cut -d' ' -f1)
[[ "$SOLL" == "$IST" ]] || { echo "Abbruch: Prüfsumme in $NAME.sha256 passt nicht zur Zip." >&2; exit 1; }

# Alte Versionen aus dem Ordner räumen, dann neue Dateien kopieren
rm -f "$ZIEL"/lichtkammer-testpaket-*.zip "$ZIEL"/lichtkammer-testpaket-*.sha256 "$ZIEL"/lichtkammer-testpaket-*.sig
cp "$ZIP" "$ZIEL/"; cp "$ZIP.sha256" "$ZIEL/"
if [[ -f "$ZIP.sig" ]]; then cp "$ZIP.sig" "$ZIEL/"; echo "Signatur mitkopiert."; else echo "Hinweis: keine .sig neben der Zip, der Signaturabschnitt bleibt 'noch nicht aktiv'."; fi
# Die PDF-Anleitung kommt aus dem Paket selbst, damit Download und Paket gleich sind
unzip -p "$ZIP" '*/Lichtkammer-Anleitung.pdf' > "$ZIEL/Lichtkammer-Anleitung.pdf"
[[ -s "$ZIEL/Lichtkammer-Anleitung.pdf" ]] || { echo "Abbruch: Keine PDF im Paket gefunden." >&2; exit 1; }
[[ -f "$ZIEL/allowed_signers" ]] || echo "Hinweis: $ZIEL/allowed_signers fehlt noch (öffentlicher Schlüssel, kommt mit dem Schlüssel)."
echo "Fertig: $NAME ($(du -h "$ZIEL/$NAME" | cut -f1)). Weiter: python3 src/build.py"
