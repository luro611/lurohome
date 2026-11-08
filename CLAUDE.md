# lurohome.de

Statische Website von Lutz (luro): Übersicht der Hobbyprojekte, je eine Projektseite, Beitrag „Vibecoding“, Tipps aus dem Repo `homelab-tipps`. Deutsch und Englisch (`<span lang="de">…</span><span lang="en">…</span>`), hell und dunkel, keine Cookies, kein Tracking, keine externen Schriften. Aufbau und Befehle: [README.md](README.md).

## Design und Marke

- Gleiche Designsprache wie MediaDB und PermLens: Farben als CSS-Variablen (`--ink`, `--accent` Terrakotta usw.), Schriften Instrument Serif, Inter, Archivo, Geist Mono. Alles in `src/style.css`.
- Marke luro: Regeln in `~/.claude/CLAUDE.md`. Logos und ihre Anleitung liegen in `logos/` (README dort). Die Startseite zeigt das **Siegel kompakt**, alle Fußzeilen die **Wortmarke** lu + kursives ro. `build.py` liest das Siegel aus `logos/svg/luro-siegel-kompakt-farbvariabel.svg`. Logos neu erzeugen mit `logos/erzeugen.py` (Befehl im logos-README, läuft in einem Debian-Container).

## Bauen und versionieren

1. `python3 src/build.py` baut `dist/` und `lurohome-website-<Datum>.zip`. Version und Commit stehen in jeder Fußzeile („Stand …“, Version und Commit im Tooltip).
2. Zeigt der Browser nach dem Upload die alte Seite: Zwischenspeicher. In Safari hilft ⌥⌘R.

## Was Claude darf (feste Regeln, Entscheidung von Lutz, 08.11.2026)

**Allein, ohne Rückfrage:**
- Versionsnummern und Projektstände anderer Projekte nachziehen (z. B. MediaDB-Version, Lenkwerk-Stufe im Fahrplan)
- Links korrigieren oder ergänzen, Datumsangaben aktualisieren
- committen und einen Probelauf (`./deploy.sh`) machen

**Nur mit OK von Lutz:**
- neue oder umgeschriebene Texte
- Impressum und Datenschutzerklärung
- Gestaltung (CSS, Aufbau, Logos, Bilder)
- **jeder Upload** (`./deploy.sh --jetzt`): erst Probelauf zeigen, dann auf ausdrückliche Freigabe warten. Eine Freigabe gilt nur für diesen einen Upload.

**Nie:** Passwörter eingeben oder in Dateien schreiben, über GitHub Actions oder andere Automatik hochladen, mit `--delete` auf dem Server löschen.

## Hochladen

```
./deploy.sh          # Probelauf: baut dist/ und zeigt, was übertragen würde
./deploy.sh --jetzt  # erst nach Freigabe: hochladen, live prüfen (curl), Tag web-<Version> setzen und pushen
```

- Zugang in `.env` (nicht versioniert, Vorlage `.env.beispiel`): `ZUGANG=ssh` mit dem Host `lurohome-kas` aus `~/.ssh/config` (Schlüssel `~/.ssh/id_ed25519_allinkl`) oder `ZUGANG=ftps` mit `lftp` und einem FTP-Benutzer nur für den Ordner dieser Domain (Passwort in `~/.netrc` oder Eingabe durch Lutz).
- `--jetzt` bricht ab, wenn `src/` nicht committet ist. Nach dem Upload vergleicht das Skript die Version auf der Seite mit `dist/` und setzt erst dann das Tag.
- **Version = Datum** (`2026.11.08`, am selben Tag `-2`, `-3` …), steht als `Version … · <Commit>` in jeder Seite. Online prüfen: `curl -sS https://lurohome.de/ | grep -o 'Version 20[^"]*'`.
- Das Skript ist bei allen drei Seiten (rothe-it, lurohome, lenkwerk-eu) bis auf den Kopf gleich. Änderungen am Ablauf in allen dreien nachziehen.
- Wöchentliche Prüfung: geplante Aufgabe „Webseiten-Wochenprüfung“ (montags 7 Uhr, Skript `../werkzeuge/wochenpruefung.py`). Sie bereitet nur vor und berichtet, sie lädt nie hoch.

## Inhalte aus anderen Projekten

- **PermLens:** Die Texte stehen in `Proxmox-Permission-Manager/docs/homepage-text.md`, der Abschnitt „Was PermLens auf deinem Host tut“ (`src/permlens.html#host`) richtet sich nach `docs/SICHERHEIT.md` dort. Ändert sich das Einrichtungs-Script oder der Wächter, muss der Abschnitt mitgezogen werden. Kein GitHub-Link, solange `luro611/permlens` privat ist (`repo=None` in `build.py`).
- **MediaDB:** Die Version liest `build.py` aus `mediadb/VERSION`. Online prüfen: Startseite muss `Version <mediadb/VERSION>` zeigen, sonst neu bauen und Probelauf.
- **Tipps:** kommen aus dem Repo `homelab-tipps` (neben lurohome oder eine Ebene höher), Liste `TIPPS` in `build.py`.

## Arbeitsweise mit Lutz

Lutz ist Einsteiger: vor Befehlen kurz Ziel und Grund nennen, bei Wahlmöglichkeiten ihn entscheiden lassen. Ein Chat pro Thema. Wechselt das Thema auf ein anderes Projekt, einen eigenen Chat in dessen Ordner vorschlagen.
