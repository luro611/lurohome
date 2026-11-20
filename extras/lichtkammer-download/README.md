# Lichtkammer-Download (lurohome.de/lichtkammer/download/)

In diesem Ordner liegen die Dateien, die `src/build.py` nach `dist/lichtkammer/` kopiert und die `./deploy.sh` mit hochlädt. Sie stehen **nicht in git** (außer `allowed_signers`).

| Datei | Wohin auf dem Server |
|---|---|
| `lichtkammer-testpaket-<Version>.zip` | `/lichtkammer/download/` |
| `….zip.sha256` | `/lichtkammer/download/` |
| `….zip.sig` (Signatur, optional) | `/lichtkammer/download/` |
| `Lichtkammer-Anleitung.pdf` | `/lichtkammer/download/` |
| `allowed_signers` (öffentlicher Schlüssel, optional, **wird committet**) | `/lichtkammer/allowed_signers` |

## Neues Paket einspielen

```
extras/lichtkammer-paket-holen.sh            # holt das neueste Paket aus ../lichtkammer/dist (Pfad als Argument änderbar)
python3 src/build.py                         # baut dist/, die Seite zeigt Version, Größe, Datum und SHA-256 selbst
./deploy.sh                                  # Probelauf, erst nach Freigabe: ./deploy.sh --jetzt
```

Die Seite liest alles aus den Dateien hier: Version aus dem Dateinamen, SHA-256 aus der `.sha256` (build.py bricht ab, wenn sie nicht zur Zip passt), Größe und Datum aus der Zip. Ältere Versionen löscht das Skript aus diesem Ordner, sie bleiben aber auf dem Server stehen (deploy.sh löscht dort nichts).

## Signatur

Der Signaturabschnitt der Seite ist nur dann „aktiv“, wenn **beide** da sind: `….zip.sig` und `allowed_signers`. Sonst steht dort „noch nicht aktiv“, und die Prüfsumme bleibt der Weg 1.

- Signieren (Lichtkammer-Ordner): `tools/signieren.sh dist/lichtkammer-testpaket-<Version>.zip`, die Schlüsselanleitung steht in `lichtkammer/docs/betrieb/Signatur-Schluessel.md`.
- Die Zeile für `allowed_signers` gibt `signieren.sh` am Ende aus (Kennung `luro@lurohome.de`, Namespace `lichtkammer`); die Datei hier ablegen und committen. Die Kennung steht in `build.py` als `LK_SIG_ID`.
- Das Skript `extras/lichtkammer-paket-holen.sh` kopiert die `.sig` mit, wenn sie neben der Zip in `dist/` liegt.
