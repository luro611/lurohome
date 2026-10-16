# Umzug von mediadb.lurohome.de nach lurohome.de

Einmalig, im ALL-INKL-Kundenmenü (KAS) und per FTP. Unterordner müssen **nicht** im KAS angelegt werden, sie kommen mit der Zip.

## 1. Hauptdomain prüfen
1. KAS → *Domain* → bei **lurohome.de** auf *bearbeiten*.
2. Nachsehen, welcher **Zielordner** eingetragen ist (z. B. `/lurohome.de/` oder `/`). Liegt dort schon etwas, das du behalten willst, erst sichern.
3. **SSL-Schutz**: Let's Encrypt einschalten (falls noch nicht), am besten mit „SSL erzwingen“, damit immer `https://` verwendet wird. Das Zertifikat braucht oft ein paar Minuten.

## 2. Website hochladen
1. `python3 src/build.py` ausführen (oder die fertige Zip nehmen).
2. Zip auspacken und den **Inhalt** (`index.html`, `impressum.html`, Ordner `mediadb/` und `fonts/`) per FTP in den Zielordner aus Schritt 1 laden.
3. Prüfen: `https://lurohome.de`, `https://lurohome.de/mediadb/`, `https://lurohome.de/impressum.html`.

## 3. Alte Adresse weiterleiten (erst wenn Schritt 2 klappt)
**Variante A, im KAS:** *Domain* → *Subdomains* → **mediadb.lurohome.de** bearbeiten → statt Ordner eine **Weiterleitung** auf `https://lurohome.de/mediadb/` eintragen (Art: dauerhaft / 301).

**Variante B, per Datei:** Die Datei `extras/mediadb-subdomain/.htaccess` per FTP in den bisherigen Ordner der Subdomain laden (vorhandene `.htaccess` dort vorher ansehen). Die alten Dateien `index.html` und `impressum.html` darin kannst du danach löschen.

Prüfen: `https://mediadb.lurohome.de` muss auf `https://lurohome.de/mediadb/` springen.

Hinweis: Dateien, die mit einem Punkt beginnen (`.htaccess`), zeigt der Finder und mancher FTP-Client nicht an. Im Finder blendet **Cmd + Shift + .** sie ein.
