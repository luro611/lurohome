# lurohome.de

Quelle der Website [lurohome.de](https://lurohome.de): eine Übersicht meiner Hobbyprojekte und je eine Projektseite, zum Beispiel [lurohome.de/mediadb](https://lurohome.de/mediadb/). Statische Seiten ohne Cookies, Tracking oder externe Schriften, auf Deutsch und Englisch.

## Aufbau
- `src/home.html`: Übersichtsseite (die Projektkarten trägt `build.py` ein)
- `src/<projekt>.html`: Projektseite, landet unter `lurohome.de/<projekt>/`, zum Beispiel `src/mediadb.html`
- `src/impressum.html`: Impressum, Haftungshinweis und Datenschutz für alle Seiten
- `src/style.css`, `src/script.js`, `src/fonts/`: Gestaltung, Sprach- und Farbumschalter, Schriften (alle Seiten teilen sie)
- `extras/mediadb-subdomain/.htaccess`: Weiterleitung der alten Adresse mediadb.lurohome.de

## Bauen
```
python3 src/build.py
```
Das erzeugt `dist/` und `lurohome-website-<Datum>.zip`. Die Versionsnummer von MediaDB liest das Skript aus `../mediadb/VERSION`, wenn der Ordner daneben liegt.

## Hochladen
Den **Inhalt** der Zip (bzw. von `dist/`) per FTP in den Ordner der Hauptdomain lurohome.de laden. Es wird immer die ganze Seite hochgeladen; vorhandene Dateien einfach überschreiben. Schritt für Schritt: [UMZUG.md](UMZUG.md).

## Neues Projekt aufnehmen
1. In `src/build.py` bei `PROJEKTE` einen Eintrag ergänzen (Ordner, Name, Kurzbeschreibung, Codeberg-Repo, Lizenz).
2. `src/<ordner>.html` anlegen (Vorlage: `src/mediadb.html`), Links zum Impressum mit `../impressum.html`, den Haftungshinweis mitnehmen.
3. In `build.py` bei `SEITEN` eintragen, bauen, hochladen.

## Haftungshinweis
Die hier vorgestellten Programme sind private Hobbyprojekte und werden kostenlos als freie Software bereitgestellt, jeweils unter der Lizenz des Projekts. Eine Gewährleistung wird nicht übernommen, soweit das gesetzlich zulässig ist. Die Nutzung erfolgt auf eigenes Risiko. Die Programme sind nicht in allen Umgebungen getestet. Es besteht keine Verpflichtung zu Support, Fehlerbehebung oder Weiterentwicklung.

Die Schriften stehen unter der SIL Open Font License, siehe `src/fonts/LIZENZEN.txt`.
