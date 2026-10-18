# luro-Logos

**lu**(tz) **ro**(the): „lu“ aufrecht in Tintenfarbe, „ro“ kursiv in Terrakotta. Schrift Instrument Serif, beim Terminal-Logo Geist Mono. Die Buchstaben sind in allen Dateien als **Umrisse** gespeichert, die Logos sehen also überall gleich aus, auch ohne installierte Schrift.

| Logo | Datei | Wofür |
|---|---|---|
| Wortmarke | `luro-wortmarke-hell` / `-dunkel` | Text, Fußzeilen, Signatur |
| Siegel | `luro-siegel-hell` / `-dunkel` | Logo auf der Website, README, Profilbild |
| Siegel kompakt | `luro-siegel-kompakt-hell` / `-dunkel` | wie das Siegel, gleiche Schrift, Ringe etwa 15 % enger |
| Terminal | `luro-terminal` | Technik-Seiten, Homelab, Präsentationen (eigene dunkle Kachel) |

**Gewählt (2026-10-18):** Siegel kompakt als Logo, Wortmarke in den Fußzeilen.

`luro-siegel-kompakt-farbvariabel.svg` (nur in `svg/`) hat keine festen Farben, sondern die Klassen `lr`, `li`, `la`, `lm`. Es wird inline in Webseiten eingebaut und übernimmt dann die Farben der Seite, hell wie dunkel. lurohome liest es beim Bauen von hier, PermLens hat eine Kopie in `app/templates/_luro_siegel.svg`.

`hell` ist für helle Hintergründe, `dunkel` für dunkle. Der Hintergrund ist durchsichtig, außer beim Terminal-Logo.

## Formate

- **`svg/`**: das Original, beliebig skalierbar. Für Webseiten und zum Weiterbearbeiten (Illustrator, Affinity, Inkscape, Figma öffnen SVG direkt).
- **`pdf/`**: Vektor, für Druck und Illustrator.
- **`png/`**: Bilder in 512 und 1024 Pixel Breite, für GitHub-Profil, Social Media und Programme, die kein SVG können.

Eine `.ai`-Datei gibt es nicht. Das ist das eigene Format von Adobe Illustrator und lässt sich nur dort sauber erzeugen. Illustrator öffnet SVG und PDF aber ohne Verlust und speichert sie auf Wunsch als `.ai`.

## Farben

| | Hell | Dunkel |
|---|---|---|
| Tinte („lu“) | `#242321` | `#f6f0e8` |
| Terrakotta („ro“, Ringe) | `#c75d3b` | `#e47a55` |
| Grau (HOMELAB, `~/`) | `#77736c` | `#b8aea4` |

Die Farben sind dieselben wie bei MediaDB, PermLens und lurohome.

## Neu erzeugen

`erzeugen.py` liest die Schriften aus `src/fonts/` und schreibt die SVGs. PNG und PDF entstehen daraus mit `rsvg-convert`. Am einfachsten in einem Debian-Container, so ist es entstanden:

```bash
docker run --rm -v "$PWD":/w -w /w debian:13 bash -c 'apt-get -qq update && apt-get -qq install -y python3-fonttools librsvg2-bin >/dev/null && python3 logos/erzeugen.py src/fonts /tmp/l && cd /tmp/l && for f in *.svg; do b=${f%.svg}; cp $f /w/logos/svg/; rsvg-convert -f pdf -o /w/logos/pdf/$b.pdf $f; rsvg-convert -w 1024 -o /w/logos/png/$b-1024.png $f; rsvg-convert -w 512 -o /w/logos/png/$b-512.png $f; done'
```

Im lurohome-Ordner ausführen. Die Schriften stehen unter der SIL Open Font License. Logos, die mit ihnen gestaltet sind, dürfen frei verwendet werden.
