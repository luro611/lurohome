"""Baut die Website lurohome.de in dist/ und als Zip zum Hochladen per FTP.
Aufruf im Projektordner:  python3 src/build.py

Neues Projekt: unten in PROJEKTE eintragen, eine Seite src/<ordner>.html anlegen
(Vorlage: src/mediadb.html) und in SEITEN ergänzen."""
import datetime, shutil, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; DIST=ROOT/'dist'

def version(projekt, ersatz=''):
    """Version aus dem Projektordner lesen (../mediadb/VERSION oder ../../mediadb/VERSION), sonst Ersatzwert."""
    for f in (ROOT.parent/projekt/'VERSION', ROOT.parent.parent/projekt/'VERSION'):
        if f.exists(): return f.read_text().strip()
    return ersatz

# Karten auf der Übersichtsseite: Ordner, Name (HTML), Kurzbeschreibung DE/EN, GitHub-Repo, Lizenz
PROJEKTE=[
  dict(ordner='mediadb', name='Media<em>DB</em>', version=version('mediadb'), lizenz='GPL-3.0', repo='luro611/mediadb',
       de='Mediendatenbank fürs Heimnetz: CDs und Musikdateien, Filme, Serien und Bücher. Barcode scannen, Daten und Cover kommen von selbst. Läuft im Docker-Container, Bedienung im Browser.',
       en='A media database for your home network: CDs and music files, films, TV shows and books. Scan a barcode and the data and covers fill in. Runs in a Docker container, used in the browser.'),
  # Repo noch privat: kein GitHub-Knopf (repo=None), Status statt Version. VERSION liegt in ../Proxmox-Permission-Manager
  dict(ordner='permlens', name='Perm<em>Lens</em>', version=version('Proxmox-Permission-Manager'), lizenz='GPL-3.0', repo=None,
       status=('In Entwicklung','In development'),
       de='Rechte-Manager für LXC-Container, derzeit speziell für Proxmox VE. Zeigt, welche Benutzer es in deinen Containern gibt, wer sie auf dem Host sind und wer auf welche eingehängten Ordner und NAS-Freigaben zugreifen darf.',
       en='A permission manager for LXC containers, currently built specifically for Proxmox VE. Shows which users exist in your containers, who they are on the host and who may access which mounted folders and NAS shares.'),
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
    if p.get('status'): kicker=f'<span lang="de">{p["status"][0]}</span><span lang="en">{p["status"][1]}</span>'
    else: kicker='Version'+(f" {p['version']}" if p['version'] else '')
    github=(f'<a class="btn ghost" href="https://github.com/{p["repo"]}" target="_blank" rel="noopener noreferrer">GitHub</a>' if p['repo'] else '')
    return (f'''    <article class="project">
      <p class="kicker">{kicker} · {p['lizenz']}</p>
      <h3>{p['name']}</h3>
      <p><span lang="de">{p['de']}</span><span lang="en">{p['en']}</span></p>
      <div class="actions"><a class="btn" href="{p['ordner']}/"><span lang="de">Zur Projektseite</span><span lang="en">Project page</span></a>{github}</div>
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
                   {'<!--EAN-->':ean_svg(),'<!--VERSION-->':version('mediadb')}),
        'permlens':('PermLens','PermLens – Rechte-Manager für LXC-Container, derzeit speziell für Proxmox VE. Zeigt Benutzer, UID-Mapping, Mounts und Freigaben. In Entwicklung.',{}),
        'vibecoding':('Vibecoding: Mein Segen, meine Zweifel und meine Sucht · lurohome','Warum meine Programme KI-generiert sind, wem der Code gehört und weshalb ich ihn als Open Source weitergebe.',{})}
for ordner,(title,desc,platz) in SEITEN.items():
    body=(HERE/f'{ordner}.html').read_text(encoding='utf-8')
    for k,v in platz.items(): body=body.replace(k,v)
    (DIST/ordner).mkdir()
    (DIST/ordner/'index.html').write_text(page(title,desc,body,tiefe=1),encoding='utf-8')

# Tipps: Anleitungen aus dem Repo homelab-tipps (liegt neben lurohome oder eine Ebene höher), DE und EN als Markdown
TIPPS_REPO='luro611/homelab-tipps'
TIPPS=[
  dict(ordner='docker-hawser-lxc', thema='Proxmox · LXC · Docker',
       titel=('Docker und Hawser in einem Debian-13-LXC für Dockhand installieren','Installing Docker and Hawser in a Debian 13 LXC for Dockhand'),
       de='Ein Skript bereitet einen vorhandenen Debian-13-LXC vor: Docker installieren, Ordnerstruktur anlegen, Hawser-Agent starten. Danach lässt sich der LXC in Dockhand als Node eintragen.',
       en='A script prepares an existing Debian 13 LXC: install Docker, create a folder structure, start the Hawser agent. The LXC can then be added to Dockhand as a node.',
       dateien=('anleitung.md','guide.en.md','install-docker.sh')),
]

def tipps_ordner():
    for d in (ROOT.parent/'homelab-tipps', ROOT.parent.parent/'homelab-tipps'):
        if d.exists(): return d
    raise SystemExit('Ordner homelab-tipps nicht gefunden (neben lurohome oder eine Ebene höher).')

def md_html(md, basis):
    """Kleiner Markdown-Umsetzer für die Anleitungen: Überschriften, Absätze, Listen, Codeblöcke, Hinweise.
    Die erste #-Überschrift ist der Seitentitel und wird übersprungen. Relative Links zeigen auf GitHub (basis)."""
    import html, re
    emoji=re.compile('[←-⯿☀-➿️‍\U0001F000-\U0001FAFF]')
    def inline(s):
        s=html.escape(s,quote=False)
        s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
        s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
        def link(m):
            url=m.group(2) if re.match(r'https?://',m.group(2)) else basis+m.group(2)
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>'
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
    out=[]; zeilen=md.split('\n'); i=0; titel=True
    while i<len(zeilen):
        z=zeilen[i]
        if z.startswith('```'):
            j=i+1
            while not zeilen[j].startswith('```'): j+=1
            out.append('<pre><code>'+html.escape('\n'.join(zeilen[i+1:j]),quote=False)+'</code></pre>'); i=j+1; continue
        m=re.match(r'(#{1,3}) (.*)',z)
        if m:
            text=emoji.sub('',m.group(2)).strip()
            if titel: titel=False
            else: out.append(f'<h{2 if len(m.group(1))<3 else 3}>{inline(text)}</h{2 if len(m.group(1))<3 else 3}>')
            i+=1; continue
        if z.startswith('>'):
            block=[]
            while i<len(zeilen) and zeilen[i].startswith('>'): block.append(zeilen[i].lstrip('> ').strip()); i+=1
            out.append('<aside class="hint"><p>'+inline(emoji.sub('',' '.join(block)).strip())+'</p></aside>'); continue
        if re.match(r'(- |\d+\. )',z):
            tag='ol' if z[0].isdigit() else 'ul'; items=[]
            while i<len(zeilen) and re.match(r'(- |\d+\. )',zeilen[i]): items.append(re.sub(r'^(- |\d+\. )','',zeilen[i])); i+=1
            out.append(f'<{tag}>'+''.join(f'<li>{inline(x)}</li>' for x in items)+f'</{tag}>'); continue
        if z.strip() in ('','---'): i+=1; continue
        block=[]
        while i<len(zeilen) and zeilen[i].strip() and not re.match(r'(```|#{1,3} |>|- |\d+\. |---)',zeilen[i]): block.append(zeilen[i].strip()); i+=1
        out.append('<p>'+inline(' '.join(block))+'</p>')
    return '\n'.join(out)

def tipp_karte(t, pre=''):
    return (f'''    <article class="project">
      <p class="kicker"><span lang="de">Anleitung</span><span lang="en">Guide</span> · {t['thema']}</p>
      <h3 class="tip-title"><span lang="de">{t['titel'][0]}</span><span lang="en">{t['titel'][1]}</span></h3>
      <p><span lang="de">{t['de']}</span><span lang="en">{t['en']}</span></p>
      <div class="actions"><a class="btn" href="{pre}tipps/{t['ordner']}/"><span lang="de">Anleitung lesen</span><span lang="en">Read the guide</span></a><a class="btn ghost" href="https://github.com/{TIPPS_REPO}/tree/main/{t['ordner']}" target="_blank" rel="noopener noreferrer">GitHub</a></div>
    </article>''')

def nav(pre, zurueck):
    return (f'<nav aria-label="Navigation">\n  <a class="brand" href="{pre}">luro<em>home</em></a>\n'
            f'  <div class="links">\n    <a href="{zurueck[0]}">← <span lang="de">{zurueck[1]}</span><span lang="en">{zurueck[2]}</span></a>\n  </div>\n'
            '  <div class="pill" role="group" aria-label="Sprache / Language"><button type="button" id="lang-de" data-lang="de" aria-pressed="true">DE</button><button type="button" id="lang-en" data-lang="en" aria-pressed="false">EN</button></div>\n'
            '  <div class="pill"><button type="button" id="theme" aria-label="Farbschema wechseln">◐ Theme</button></div>\n</nav>\n')

def fuss(pre):
    return (f'<footer>\n  <span class="sp">lurohome.de</span>\n  <a href="{pre}"><span lang="de">Startseite</span><span lang="en">Home</span></a>\n'
            '  <a href="https://github.com/luro611" target="_blank" rel="noopener noreferrer">GitHub</a>\n'
            f'  <a href="{pre}impressum.html"><span lang="de">Impressum</span><span lang="en">Legal notice</span></a>\n'
            f'  <a href="{pre}impressum.html#datenschutz"><span lang="de">Datenschutz</span><span lang="en">Privacy</span></a>\n'
            '  <span><span lang="de">Keine Cookies, kein Tracking</span><span lang="en">No cookies, no tracking</span></span>\n</footer>\n')

HINWEIS=('Private Anleitung, kostenlos und ohne Gewährleistung, soweit gesetzlich zulässig. Lies das Skript, bevor du es ausführst, und probiere es zuerst in einer Testumgebung aus. Die Nutzung erfolgt auf eigenes Risiko.',
         'A private guide, free of charge and without warranty to the extent permitted by law. Read the script before you run it and try it in a test environment first. Use at your own risk.')

if TIPPS:
    quelle=tipps_ordner()
    (DIST/'tipps').mkdir()
    uebersicht=('<div class="shell">\n'+nav('../',('../','Startseite','Home'))+
        '<section class="tips-page">\n  <p class="eyebrow"><span lang="de">Tipps</span><span lang="en">Tips</span></p>\n'
        '  <h1><span lang="de">Anleitungen <em>fürs Homelab</em></span><span lang="en">Guides <em>for the homelab</em></span></h1>\n'
        '  <div class="projects">\n'+'\n'.join(tipp_karte(t,'../') for t in TIPPS).replace('href="../tipps/','href="')+'\n  </div>\n</section>\n'+fuss('../')+'</div>')
    (DIST/'tipps'/'index.html').write_text(page('Tipps · lurohome','Anleitungen und Skripte fürs Homelab: Proxmox, LXC, Docker.',uebersicht,tiefe=1),encoding='utf-8')
    for t in TIPPS:
        de_md,en_md,skript=t['dateien']; src=quelle/t['ordner']
        blob=f"https://github.com/{TIPPS_REPO}/blob/main/{t['ordner']}/"; raw=f"https://raw.githubusercontent.com/{TIPPS_REPO}/main/{t['ordner']}/"
        teile=[]
        for lang,md,ti,hw,lbl in (('de',de_md,t['titel'][0],HINWEIS[0],('Anleitung als Markdown','Skript herunterladen','Auf GitHub')),
                                  ('en',en_md,t['titel'][1],HINWEIS[1],('Guide as Markdown','Download script','On GitHub'))):
            body=md_html((src/md).read_text(encoding='utf-8'),blob)
            teile.append(f'''<div lang="{lang}">
<header class="essay-head">
  <p class="eyebrow">{'Tipp' if lang=='de' else 'Tip'} · {t['thema']}</p>
  <h1>{ti}</h1>
  <p class="note">{hw}</p>
  <p class="actions"><a class="btn" href="{raw}{skript}" download>{lbl[1]}</a><a class="btn ghost" href="{blob}{md}" target="_blank" rel="noopener noreferrer">{lbl[0]}</a><a class="btn ghost" href="https://github.com/{TIPPS_REPO}" target="_blank" rel="noopener noreferrer">{lbl[2]}</a></p>
</header>
<div class="essay-body guide">
{body}
</div>
</div>''')
        seite=('<div class="shell">\n'+nav('../../',('../','Alle Tipps','All tips'))+'<article class="essay" id="top">\n'+'\n'.join(teile)+'\n</article>\n'+fuss('../../')+'</div>')
        (DIST/'tipps'/t['ordner']).mkdir()
        (DIST/'tipps'/t['ordner']/'index.html').write_text(page(f"{t['titel'][0]} · lurohome",t['de'],seite,tiefe=2),encoding='utf-8')
    # Karten auf der Startseite (Platzhalter in home.html)
    idx=DIST/'index.html'; idx.write_text(idx.read_text(encoding='utf-8').replace('<!--TIPPS-->','\n'.join(tipp_karte(t) for t in TIPPS)),encoding='utf-8')

z=ROOT/f'lurohome-website-{datetime.date.today().isoformat()}.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(DIST.rglob('*')):
        if f.is_file(): zf.write(f,f.relative_to(DIST).as_posix())
print('fertig:',z)
