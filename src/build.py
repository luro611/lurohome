"""Baut die Website lurohome.de in dist/ und als Zip zum Hochladen per FTP.
Aufruf im Projektordner:  python3 src/build.py

Neues Projekt: unten in PROJEKTE eintragen, eine Seite src/<ordner>.html anlegen
(Vorlage: src/mediadb.html) und in SEITEN ergänzen."""
import datetime, shutil, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; DIST=ROOT/'dist'

def version(projekt, ersatz=''):
    """Version aus dem Nachbarordner lesen (z. B. ../mediadb/VERSION), sonst Ersatzwert."""
    f=ROOT.parent/projekt/'VERSION'
    return f.read_text().strip() if f.exists() else ersatz

# Karten auf der Übersichtsseite: Ordner, Name (HTML), Kurzbeschreibung DE/EN, GitHub-Repo, Lizenz
PROJEKTE=[
  dict(ordner='mediadb', name='Media<em>DB</em>', version=version('mediadb'), lizenz='GPL-3.0', repo='luro611/mediadb',
       de='Mediendatenbank fürs Heimnetz: CDs und Musikdateien, Filme, Serien und Bücher. Barcode scannen, Daten und Cover kommen von selbst. Läuft im Docker-Container, Bedienung im Browser.',
       en='A media database for your home network: CDs and music files, films, TV shows and books. Scan a barcode and the data and covers fill in. Runs in a Docker container, used in the browser.'),
]

FONTS=[('Instrument','InstrumentSerif-Regular.ttf','400','normal'),('Instrument','InstrumentSerif-Italic.ttf','400','italic'),
  ('Inter','Inter-Variable.ttf','100 900','normal'),('Inter','Inter-VariableItalic.ttf','100 900','italic'),
  ('Archivo','Archivo-Variable.ttf','100 900','normal'),('GeistMono','GeistMono-Variable.ttf','100 900','normal')]
style=(HERE/'style.css').read_text(encoding='utf-8')
script='<script>\n'+(HERE/'script.js').read_text(encoding='utf-8')+'</script>'

def page(title, desc, body, tiefe=0):
    pre='../'*tiefe
    fonts=''.join(f"@font-face{{font-family:{a};src:url('{pre}fonts/{f}') format('truetype');font-weight:{w};font-style:{s};font-display:swap}}" for a,f,w,s in FONTS)
    return ('<!doctype html>\n<html lang="de" data-lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<title>{title}</title>\n<meta name="description" content="{desc}">\n'
            f'<style>{fonts}</style>\n<style>\n{style}</style>\n</head>\n<body>\n{body}\n{script}\n</body>\n</html>\n')

def karte(p):
    v=f" {p['version']}" if p['version'] else ''
    return (f'''    <article class="project">
      <p class="kicker">Version{v} · {p['lizenz']}</p>
      <h3>{p['name']}</h3>
      <p><span lang="de">{p['de']}</span><span lang="en">{p['en']}</span></p>
      <div class="actions"><a class="btn" href="{p['ordner']}/"><span lang="de">Zur Projektseite</span><span lang="en">Project page</span></a><a class="btn ghost" href="https://github.com/{p['repo']}" target="_blank" rel="noopener noreferrer">GitHub</a></div>
    </article>''')
soon=('    <article class="project soon"><p class="kicker"><span lang="de">Demnächst</span><span lang="en">Coming soon</span></p>'
      '<p><span lang="de">Weitere Projekte folgen.</span><span lang="en">More projects to come.</span></p></article>')

def ean_svg(code='4006381333931'):
    """EAN-13 Barcode (Beispielnummer) als SVG für die MediaDB-Seite"""
    L=['0001101','0011001','0010011','0111101','0100011','0110001','0101111','0111011','0110111','0001011']
    R=[''.join('1' if c=='0' else '0' for c in x) for x in L]; G=[x[::-1] for x in R]
    PAR=['LLLLLL','LLGLGG','LLGGLG','LLGGGL','LGLLGG','LGGLLG','LGGGLL','LGLGLG','LGLGGL','LGGLGL']
    bits='101'+''.join((L if PAR[int(code[0])][i]=='L' else G)[int(c)] for i,c in enumerate(code[1:7]))+'01010'+''.join(R[int(c)] for c in code[7:])+'101'
    guard=set(range(0,3))|set(range(45,50))|set(range(92,95)); rects=[]; i=0
    while i<95:
        if bits[i]=='1':
            j=i
            while j<95 and bits[j]=='1' and ((j in guard)==(i in guard)): j+=1
            rects.append(f'<rect x="{i+11}" y="0" width="{j-i}" height="{74 if i in guard else 66}"/>'); i=j
        else: i+=1
    return (f'<svg class="ean" viewBox="0 0 117 82" role="img" aria-label="EAN-13 {code}"><g class="bars">{"".join(rects)}</g>'
            f'<g class="digits"><text x="5" y="80">{code[0]}</text><text x="35" y="80">{code[1:7]}</text><text x="82" y="80">{code[7:]}</text></g></svg>')

if DIST.exists(): shutil.rmtree(DIST)
(DIST/'fonts').mkdir(parents=True)
for f in (HERE/'fonts').iterdir(): shutil.copy2(f,DIST/'fonts'/f.name)

home=(HERE/'home.html').read_text(encoding='utf-8').replace('<!--PROJEKTE-->','\n'.join([karte(p) for p in PROJEKTE]+[soon]))
(DIST/'index.html').write_text(page('lurohome – Hobbyprojekte','Private Hobbyprojekte fürs Heimnetz, freie Software auf GitHub. Darunter MediaDB, eine Mediendatenbank für CDs, Filme, Serien und Bücher.',home),encoding='utf-8')

legal=(HERE/'impressum.html').read_text(encoding='utf-8')
legal_body=('<div class="shell">\n<nav aria-label="Navigation"><a class="brand" href="./">luro<em>home</em></a>'
            '<a class="back" href="./">← Zur Startseite</a>'
            '<div class="pill"><button type="button" id="theme" aria-label="Farbschema wechseln">◐ Theme</button></div></nav>\n'
            +legal+'\n<footer><span class="sp">lurohome.de</span><a href="./">Startseite</a><span>Keine Cookies, kein Tracking</span></footer>\n</div>')
(DIST/'impressum.html').write_text(page('Impressum · lurohome','Impressum und Datenschutzerklärung von lurohome.de.',legal_body),encoding='utf-8')

# Projektseiten: Ordner -> (Titel, Beschreibung, Platzhalter)
SEITEN={'mediadb':('MediaDB','MediaDB – selbst gehostete Datenbank für CDs, Musikdateien, Filme, Serien und Bücher. Läuft im Heimnetz, Daten bleiben bei dir.',
                   {'<!--EAN-->':ean_svg(),'<!--VERSION-->':version('mediadb')})}
for ordner,(title,desc,platz) in SEITEN.items():
    body=(HERE/f'{ordner}.html').read_text(encoding='utf-8')
    for k,v in platz.items(): body=body.replace(k,v)
    (DIST/ordner).mkdir()
    (DIST/ordner/'index.html').write_text(page(title,desc,body,tiefe=1),encoding='utf-8')

z=ROOT/f'lurohome-website-{datetime.date.today().isoformat()}.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(DIST.rglob('*')):
        if f.is_file(): zf.write(f,f.relative_to(DIST).as_posix())
print('fertig:',z)
