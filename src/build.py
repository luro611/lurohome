"""Baut die Website lurohome.de in dist/ und als Zip zum Hochladen per FTP.
Aufruf im Projektordner:  python3 src/build.py

Neues Projekt: unten in PROJEKTE eintragen, eine Seite src/<ordner>.html anlegen
(Vorlage: src/mediadb.html) und in SEITEN ergänzen."""
import datetime, json, re, shutil, subprocess, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; DIST=ROOT/'dist'
SITE='https://lurohome.de/'
HEUTE=datetime.date.today().isoformat()

# Version der Website = Datum (CalVer): 2026.10.18, bei mehreren Uploads am selben Tag 2026.10.18-2 usw.
# Jeder Upload bekommt danach ein Git-Tag web-<Version> (Befehl steht am Ende der Ausgabe).
def git(*args):
    try: return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True,timeout=10).stdout.strip()
    except (OSError,subprocess.TimeoutExpired): return ''
def website_version():
    basis=datetime.date.today().strftime('%Y.%m.%d'); head=git('rev-parse','HEAD')
    for n in range(1,100):
        v=basis if n==1 else f'{basis}-{n}'
        ziel=git('rev-list','-n1',f'web-{v}')
        if not ziel or ziel==head: return v, bool(ziel)
    return basis, False
VERSION, SCHON_GETAGGT = website_version()
COMMIT = git('rev-parse','--short','HEAD') or '?'
GEAENDERT = bool(git('status','--porcelain','--','src','logos'))  # Website-Dateien nicht committet
_d=datetime.date.today()
STAND=(f'<span title="Version {VERSION} · {COMMIT}{"+" if GEAENDERT else ""}"><span lang="de">Stand {_d:%d.%m.%Y}</span>'
       f'<span lang="en">Updated {_d.day} {_d:%b %Y}</span></span>')

def version(projekt, ersatz=''):
    """Version aus dem Projektordner lesen (../mediadb/VERSION oder ../../mediadb/VERSION), sonst Ersatzwert."""
    for f in (ROOT.parent/projekt/'VERSION', ROOT.parent.parent/projekt/'VERSION'):
        if f.exists(): return f.read_text().strip()
    return ersatz

# Karten auf der Übersichtsseite: Ordner, Name (HTML), Kurzbeschreibung DE/EN, GitHub-Repo, Lizenz
PROJEKTE=[
  dict(ordner='mediadb', name='Media<em>DB</em>', version=version('mediadb'), lizenz='GPL-3.0', repo='luro611/mediadb',
       de='Mediendatenbank fürs Heimnetz: CDs und Musikdateien, Filme, Serien und Bücher. Barcode scannen, Daten und Cover kommen von selbst. Für den ganzen Haushalt, mit eigenem Profil, eigener Bewertung und „gesehen“ für jede Person. Läuft im Docker-Container, Bedienung im Browser.',
       en='A media database for your home network: CDs and music files, films, TV shows and books. Scan a barcode and the data and covers fill in. For the whole household, with a profile, ratings and “watched” for each person. Runs in a Docker container, used in the browser.'),
  # Öffentlich seit 1.0.0 (luro611/permlens). Texte aus Proxmox-Permission-Manager/docs/homepage-text.md, VERSION liegt dort
  dict(ordner='permlens', name='Perm<em>Lens</em>', version=version('Proxmox-Permission-Manager'), lizenz='GPL-3.0', repo='luro611/permlens',
       de='Rechte-Manager für LXC-Container, derzeit speziell für Proxmox VE. Zeigt, welche Benutzer es in deinen Containern gibt, wer sie auf dem Host sind und wer auf welche eingehängten Ordner und NAS-Freigaben zugreifen darf. PermLens findet typische Rechte-Probleme von selbst, beantwortet „Kann X hier schreiben?“ Schritt für Schritt, auch für Docker-Apps, und setzt die Lösung auf Wunsch selbst um, mit Vorschau und Rückgängig.',
       en='A permission manager for LXC containers, currently built specifically for Proxmox VE. Shows which users exist in your containers, who they are on the host and who may access which mounted folders and NAS shares. PermLens finds common permission problems on its own, answers “Can X write here?” step by step, for Docker apps too, and, if you want, applies the fix itself, with preview and undo.'),
  # Vorabversion 0.1.0-rc1, Repo luro611/lichtkammer privat bis zum öffentlichen Release, daher repo=None. Stand in lichtkammer/README.md
  dict(ordner='lichtkammer', name='Licht<em>kammer</em>', version='', lizenz='AGPL-3.0', repo=None,
       status=('Vorabversion','Pre-release'),
       de='Schlankes Open-Source-Foto-CMS für ausschließlich eigene Bilder: hochladen, automatisch verkleinern, in Galerien ordnen, Seiten aus Blöcken bauen und als fertiges HTML veröffentlichen, mit Vorschau und Rückgängig. Läuft auf einfachem Webspace mit PHP und SQLite, für den nur FTP nötig ist, oder in Docker. Verwaltung auf Deutsch, auch für Laien.',
       en='A lean open-source photo CMS for your own pictures only: upload, resize automatically, arrange in galleries, build pages from blocks and publish as ready-made HTML, with preview and undo. Runs on simple web hosting with PHP and SQLite that only needs FTP, or in Docker. German-language admin, usable by non-experts.'),
  # In Entwicklung: IPTC 0.1.0-dev (Repo luro611/iptc privat), Rotorwacht 0.6.0 (luro611/rotorwacht privat), paperless-ngx Backup in Planung ("bald")
  dict(ordner='iptc', name='IPT<em>C</em>', version='', lizenz='GPL-3.0', repo=None, status=('In Entwicklung','In development'),
       de='Zeigt alle Metadaten eines Bildes (EXIF, IPTC, XMP, Hersteller-Tags) übersichtlich, durchsuchbar und exportierbar. Bild in den Browser ziehen, fertig. Läuft im eigenen Container im Heimnetz, speichert nichts und verändert keine Originale.',
       en='Shows all metadata of a picture (EXIF, IPTC, XMP, maker tags) clearly, searchable and exportable. Drop an image into the browser, done. Runs in its own container on your home network, stores nothing and never changes originals.'),
  dict(ordner='rotorwacht', name='Rotor<em>wacht</em>', version='', lizenz='MIT', repo=None, status=('In Entwicklung · Spiel','In development · game'), os='macOS', kategorie='GameApplication',
       de='Hubschrauber-Rettungsspiel für den Mac: Nach Naturkatastrophen Menschen von Dächern und Anhöhen holen und ins Lager bringen. Sechs Einsätze, drei Stufen, Controller, Bestenliste und ein Übungsmodus. Selbst gebaut mit Swift und SpriteKit.',
       en='A helicopter rescue game for the Mac: after natural disasters, pick people up from rooftops and hilltops and bring them to the camp. Six missions, three levels, controller support, high scores and a practice mode. Built in-house with Swift and SpriteKit.'),
  dict(ordner='paperless-ngx-backup', name='paperless-ngx <em>Backup</em>', version='', lizenz='GPL-3.0', repo=None, status=('Bald','Coming soon'),
       de='Backup und Wiederherstellung für paperless-ngx mit grafischer Oberfläche: Datenbank, Dokumente und Konfiguration konsistent, verschlüsselt und prüfbar sichern und auf einem neuen LXC oder einer VM wiederherstellen. In Planung, kein offizielles paperless-ngx-Projekt.',
       en='Backup and restore for paperless-ngx with a graphical interface: back up database, documents and configuration consistently, encrypted and verifiable, and restore them on a new LXC or VM. In planning, not an official paperless-ngx project.'),
  # Buch, kein Programm (art='buch'): Repo luro611/homelab-handbuch privat bis zum Release, daher repo=None
  dict(ordner='homelab-handbuch', name='Homelab-<em>Handbuch</em>', version='', lizenz='GPL-3.0', repo=None, art='buch',
       status=('Buch · in Arbeit','Book · work in progress'),
       de='Ein Buch für Einsteiger: Schritt für Schritt zum eigenen Homeserver mit Proxmox. Jede Anwendung läuft in einem eigenen LXC, das schont Kerne und Speicher. Verwaltet wird alles bequem mit Dockhand im Browser.',
       en='A book for beginners: step by step to your own home server with Proxmox. Every application runs in its own LXC, which saves cores and memory. Everything is managed comfortably with Dockhand in the browser.'),
]

FONTS=[('Instrument','InstrumentSerif-Regular.ttf','400','normal'),('Instrument','InstrumentSerif-Italic.ttf','400','italic'),
  ('Inter','Inter-Variable.ttf','100 900','normal'),('Inter','Inter-VariableItalic.ttf','100 900','italic'),
  ('Archivo','Archivo-Variable.ttf','100 900','normal'),('GeistMono','GeistMono-Variable.ttf','100 900','normal')]
style=(HERE/'style.css').read_text(encoding='utf-8')
script='<script>\n'+(HERE/'script.js').read_text(encoding='utf-8')+'</script>'

# Für Suchmaschinen und KI-Suche: schema.org als JSON-LD. Jede Seite trägt sich beim Bauen in URLS ein (für sitemap.xml).
PERSON={'@type':'Person','@id':SITE+'#person','name':'Lutz Rothe','url':'https://rothe.it/',
        'sameAs':['https://rothe.it/','https://github.com/luro611','https://www.br-foto.com'],
        'knowsAbout':['Homelab','Proxmox VE','LXC','Docker','Open-Source-Software','Programmieren mit KI']}
WEBSITE={'@type':'WebSite','@id':SITE+'#website','url':SITE,'name':'lurohome','inLanguage':['de','en'],'publisher':{'@id':SITE+'#person'}}
URLS=[]

def software(p, beschreibung):
    """Projekt aus PROJEKTE als SoftwareApplication (oder als Book bei art='buch')"""
    if p.get('art')=='buch':
        return {'@type':'Book','@id':SITE+p['ordner']+'/#buch','name':p['name'].replace('<em>','').replace('</em>',''),
                'description':beschreibung,'url':SITE+p['ordner']+'/','inLanguage':'de','author':{'@id':SITE+'#person'},
                'isAccessibleForFree':True,'creativeWorkStatus':'Draft'}
    d={'@type':'SoftwareApplication','@id':SITE+p['ordner']+'/#software','name':p['name'].replace('<em>','').replace('</em>',''),
       'description':beschreibung,'url':SITE+p['ordner']+'/','applicationCategory':p.get('kategorie','UtilitiesApplication'),'operatingSystem':p.get('os','Linux'),
       'license':{'AGPL-3.0':'https://www.gnu.org/licenses/agpl-3.0.html','MIT':'https://opensource.org/licenses/MIT'}.get(p['lizenz'],'https://www.gnu.org/licenses/gpl-3.0.html'),'isAccessibleForFree':True,'author':{'@id':SITE+'#person'},
       'offers':{'@type':'Offer','price':'0','priceCurrency':'EUR'}}
    if p['version'] and not p.get('status'): d['softwareVersion']=p['version']
    if p['repo']: d['sameAs']='https://github.com/'+p['repo']
    return d

def kopf(title, desc, pfad, extra=()):
    url=SITE+pfad; URLS.append(url)
    seite={'@type':'WebPage','@id':url,'url':url,'name':title,'description':desc,'inLanguage':['de','en'],
           'isPartOf':{'@id':SITE+'#website'},'author':{'@id':SITE+'#person'},'dateModified':HEUTE}
    ld=json.dumps({'@context':'https://schema.org','@graph':[WEBSITE,PERSON,seite,*extra]},ensure_ascii=False,separators=(',',':'))
    pre='../'*pfad.count('/') if pfad.endswith('/') else ''
    return (f'<link rel="canonical" href="{url}">\n<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">\n'
            '<meta name="robots" content="index,follow">\n<meta name="author" content="Lutz Rothe">\n'
            '<meta property="og:type" content="website">\n<meta property="og:locale" content="de_DE">\n<meta property="og:locale:alternate" content="en_GB">\n'
            f'<meta property="og:site_name" content="lurohome">\n<meta property="og:title" content="{title}">\n<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:url" content="{url}">\n<meta name="twitter:card" content="summary">\n'
            f'<script type="application/ld+json">{ld}</script>\n')

def page(title, desc, body, tiefe=0, pfad='', extra=()):
    pre='../'*tiefe
    body=body.replace('</footer>',f'  {STAND}\n</footer>',1)  # Stand der Website in jeder Fußzeile
    fonts=''.join(f"@font-face{{font-family:{a};src:url('{pre}fonts/{f}') format('truetype');font-weight:{w};font-style:{s};font-display:swap}}" for a,f,w,s in FONTS)
    return ('<!doctype html>\n<html lang="de" data-lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<title>{title}</title>\n<meta name="description" content="{desc}">\n{kopf(title,desc,pfad,extra)}'
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
for f in (HERE/'fonts').iterdir():
    if f.is_file(): shutil.copy2(f,DIST/'fonts'/f.name)

# Logo: Siegel (kompakt) aus logos/, Farben über CSS-Variablen, damit es hell und dunkel passt
SIEGEL=(ROOT/'logos'/'svg'/'luro-siegel-kompakt-farbvariabel.svg').read_text(encoding='utf-8').strip()
home=(HERE/'home.html').read_text(encoding='utf-8').replace('<!--PROJEKTE-->','\n'.join([karte(p) for p in PROJEKTE]+[soon])).replace('<!--SIEGEL-->',SIEGEL)
(DIST/'index.html').write_text(page('lurohome – Hobbyprojekte fürs Heimnetz','Private Hobbyprojekte fürs Heimnetz, freie Software auf GitHub: MediaDB, eine Mediendatenbank für CDs, Filme, Serien und Bücher, und PermLens für Rechte in Proxmox-LXC-Containern. Dazu Homelab-Anleitungen und ein Homelab-Handbuch für Einsteiger.',home,extra=[software(p,p['de']) for p in PROJEKTE]),encoding='utf-8')

legal=(HERE/'impressum.html').read_text(encoding='utf-8')
legal_body=('<div class="shell">\n<nav aria-label="Navigation"><a class="brand" href="./">luro<em>home</em></a>'
            '<a class="back" href="./">← Zur Startseite</a>'
            '<div class="pill"><button type="button" id="theme" aria-label="Farbschema wechseln">◐ Theme</button></div></nav>\n'
            +legal+'\n<footer><a class="sp luro" href="https://lurohome.de/" aria-label="luro · lurohome.de">lu<em>ro</em></a><a href="./">Startseite</a><span>Keine Cookies, kein Tracking</span></footer>\n</div>')
(DIST/'impressum.html').write_text(page('Impressum · lurohome','Impressum und Datenschutzerklärung von lurohome.de.',legal_body,pfad='impressum.html'),encoding='utf-8')


# Lichtkammer-Testpaket: liegt NICHT in git, sondern in extras/lichtkammer-download/ (Anleitung dort in README.md).
# Befüllt wird der Ordner mit extras/lichtkammer-paket-holen.sh. Fehlt etwas, baut die Seite trotzdem:
# ohne Zip zeigt sie "gerade nicht bereit", ohne .sig oder allowed_signers ist der Signaturabschnitt "noch nicht aktiv".
LK_DIR=ROOT/'extras'/'lichtkammer-download'
LK_SIG_ID='luro@lurohome.de'   # Kennung in allowed_signers, gleich wie in der Anleitung im Paket (lichtkammer/docs/betrieb/allowed_signers)
def lichtkammer_paket():
    def mb(n,de): return f'{n/1e6:.1f}'.replace('.',',' if de else '.')+' MB'
    zips=sorted(LK_DIR.glob('lichtkammer-testpaket-*.zip'),key=lambda f:[int(x) if x.isdigit() else x for x in re.split(r'[.\-]',f.name)]) if LK_DIR.exists() else []
    d={'@@SIG_ID@@':LK_SIG_ID,'@@LK_VERSION@@':'0.1.0-rc1'}
    if not zips: return d, False, False
    z=zips[-1]; sha=Path(str(z)+'.sha256'); pdf=LK_DIR/'Lichtkammer-Anleitung.pdf'
    if not sha.exists() or not pdf.exists(): raise SystemExit(f'Lichtkammer-Paket unvollständig: {sha.name} oder Lichtkammer-Anleitung.pdf fehlt in {LK_DIR}')
    summe=sha.read_text().split()[0]
    import hashlib
    if hashlib.sha256(z.read_bytes()).hexdigest()!=summe: raise SystemExit(f'{z.name}: Prüfsumme in .sha256 passt nicht zur Datei. Paket neu holen.')
    dt=datetime.date.fromtimestamp(z.stat().st_mtime)
    d.update({'@@LK_VERSION@@':z.name[len('lichtkammer-testpaket-'):-len('.zip')],'@@LK_ZIP@@':z.name,'@@LK_SHA@@':summe,
              '@@LK_SIZE_DE@@':mb(z.stat().st_size,True),'@@LK_SIZE_EN@@':mb(z.stat().st_size,False),
              '@@LK_PDF_DE@@':mb(pdf.stat().st_size,True),'@@LK_PDF_EN@@':mb(pdf.stat().st_size,False),
              '@@LK_DATE_DE@@':f'{dt:%d.%m.%Y}','@@LK_DATE_EN@@':f'{dt.day} {dt:%b %Y}'})
    sig=(LK_DIR/(z.name+'.sig')).exists() and (LK_DIR/'allowed_signers').exists()
    return d, True, sig
LK_PLATZ, LK_DA, LK_SIG = lichtkammer_paket()
def lichtkammer_seite(body):
    def teil(name,behalten):
        nonlocal body
        body=re.sub(rf'<!--{name}-->(.*?)<!--/{name}-->',(lambda m:m.group(1)) if behalten else '',body,flags=re.S)
    teil('PAKET-DA',LK_DA); teil('PAKET-FEHLT',not LK_DA); teil('SIG-AKTIV',LK_DA and LK_SIG); teil('SIG-FEHLT',not (LK_DA and LK_SIG))
    for k,v in LK_PLATZ.items(): body=body.replace(k,v)
    return body

# Projektseiten: Ordner -> (Titel, Beschreibung, Platzhalter)
SEITEN={'mediadb':('MediaDB','MediaDB – selbst gehostete Datenbank für CDs, Musikdateien, Filme, Serien und Bücher. Läuft im Heimnetz, Daten bleiben bei dir.',
                   {'<!--EAN-->':ean_svg(),'<!--VERSION-->':version('mediadb')}),
        'permlens':('PermLens','PermLens – Rechte-Manager für LXC-Container, derzeit speziell für Proxmox VE. Zeigt Benutzer, UID-Mapping, Mounts, Freigaben und Docker-Apps und erklärt, wer wo schreiben darf. Version '+version('Proxmox-Permission-Manager')+', freie Software auf GitHub.',
                   {'<!--VERSION-->':version('Proxmox-Permission-Manager')}),
        'lichtkammer':('Lichtkammer · lurohome','Lichtkammer – schlankes Foto-CMS für eigene Bilder: Galerien, Seiten aus Blöcken, Veröffentlichen als fertiges HTML. PHP und SQLite auf einfachem Webspace oder Docker im Homelab. Testversion mit Installations- und Bedienungsanleitung, Download und Echtheitsprüfung.',{}),
        'iptc':('IPTC · lurohome','IPTC – lokale Web-Anwendung, die alle Metadaten eines Bildes (EXIF, IPTC, XMP) ausliest und übersichtlich zeigt. Läuft im Heimnetz, speichert nichts. In Entwicklung.',{}),
        'rotorwacht':('Rotorwacht · lurohome','Rotorwacht – Hubschrauber-Rettungsspiel für den Mac mit sechs Einsätzen, drei Stufen, Controller und Bestenliste. In Entwicklung.',{}),
        'paperless-ngx-backup':('paperless-ngx Backup · lurohome','paperless-ngx Backup – Backup und Wiederherstellung für paperless-ngx mit grafischer Oberfläche. Bald, in Planung.',{}),
        'homelab-handbuch':('Homelab-Handbuch · lurohome','Homelab-Handbuch – ein Buch für Einsteiger: Schritt für Schritt zum eigenen Homeserver mit Proxmox, jede Anwendung in einem eigenen LXC, verwaltet mit Dockhand. In Arbeit.',{}),
        'vibecoding':('Vibecoding: Mein Segen, meine Zweifel und meine Sucht · lurohome','Warum meine Programme KI-generiert sind, wem der Code gehört und weshalb ich ihn als Open Source weitergebe.',{})}
for ordner,(title,desc,platz) in SEITEN.items():
    body=(HERE/f'{ordner}.html').read_text(encoding='utf-8')
    for k,v in platz.items(): body=body.replace(k,v)
    if ordner=='lichtkammer': body=lichtkammer_seite(body)
    (DIST/ordner).mkdir()
    if (HERE/'bilder'/ordner).exists(): shutil.copytree(HERE/'bilder'/ordner,DIST/ordner/'bilder')  # z. B. Bildschirmfotos
    proj=[p for p in PROJEKTE if p['ordner']==ordner]
    if proj: extra=[software(proj[0],desc)]
    else: extra=[{'@type':'BlogPosting','@id':SITE+ordner+'/#beitrag','headline':title.split(' · ')[0],'description':desc,'url':SITE+ordner+'/',
                  'inLanguage':['de','en'],'author':{'@id':SITE+'#person'},'datePublished':'2026-10-17','dateModified':HEUTE}]
    (DIST/ordner/'index.html').write_text(page(title,desc,body,tiefe=1,pfad=ordner+'/',extra=extra),encoding='utf-8')


# Lichtkammer-Download: Dateien aus extras/ nach dist/lichtkammer/ (Zip, .sha256, .sig, PDF unter download/, allowed_signers daneben)
if LK_DA:
    (DIST/'lichtkammer'/'download').mkdir(parents=True,exist_ok=True)
    for f in LK_DIR.iterdir():
        if f.name=='allowed_signers': shutil.copy2(f,DIST/'lichtkammer'/f.name)
        elif f.suffix in ('.zip','.sha256','.sig','.pdf'): shutil.copy2(f,DIST/'lichtkammer'/'download'/f.name)

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
    return (f'<footer>\n  <a class="sp luro" href="https://lurohome.de/" aria-label="luro · lurohome.de">lu<em>ro</em></a>\n  <a href="{pre}"><span lang="de">Startseite</span><span lang="en">Home</span></a>\n'
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
    (DIST/'tipps'/'index.html').write_text(page('Tipps · lurohome','Anleitungen und Skripte fürs Homelab: Proxmox, LXC, Docker.',uebersicht,tiefe=1,pfad='tipps/'),encoding='utf-8')
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
        (DIST/'tipps'/t['ordner']/'index.html').write_text(page(f"{t['titel'][0]} · lurohome",t['de'],seite,tiefe=2,pfad=f"tipps/{t['ordner']}/",
            extra=[{'@type':'TechArticle','@id':SITE+f"tipps/{t['ordner']}/#anleitung",'headline':t['titel'][0],'alternativeHeadline':t['titel'][1],
                    'description':t['de'],'about':t['thema'],'url':SITE+f"tipps/{t['ordner']}/",'inLanguage':['de','en'],
                    'author':{'@id':SITE+'#person'},'dateModified':HEUTE,'sameAs':f"https://github.com/{TIPPS_REPO}/tree/main/{t['ordner']}"}]),encoding='utf-8')
    # Karten auf der Startseite (Platzhalter in home.html)
    idx=DIST/'index.html'; idx.write_text(idx.read_text(encoding='utf-8').replace('<!--TIPPS-->','\n'.join(tipp_karte(t) for t in TIPPS)),encoding='utf-8')

# Für Suchmaschinen und KI-Crawler: Sitemap, robots.txt, llms.txt, Favicon
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    +''.join(f'  <url><loc>{u}</loc><lastmod>{HEUTE}</lastmod></url>\n' for u in URLS)+'</urlset>\n',encoding='utf-8')
(DIST/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n',encoding='utf-8')
shutil.copy2(HERE/'favicon.svg',DIST/'favicon.svg')
llms=(HERE/'llms.txt').read_text(encoding='utf-8')
llms=llms.replace('<!--PROJEKTE-->','\n'.join(f"- [{p['name'].replace('<em>','').replace('</em>','')}]({SITE}{p['ordner']}/): {p['de']}"
                                               +(f" Quellcode: https://github.com/{p['repo']}" if p['repo'] else (' Testversion mit Download, Quellcode noch nicht öffentlich.' if p['ordner']=='lichtkammer' else ' Noch nicht veröffentlicht.')) for p in PROJEKTE))
llms=llms.replace('<!--TIPPS-->','\n'.join(f"- [{t['titel'][0]}]({SITE}tipps/{t['ordner']}/): {t['de']}" for t in TIPPS))
(DIST/'llms.txt').write_text(llms,encoding='utf-8')

z=ROOT/f'lurohome-website-{datetime.date.today().isoformat()}.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(DIST.rglob('*')):
        if f.is_file() and 'lichtkammer/download/' not in f.relative_to(DIST).as_posix(): zf.write(f,f.relative_to(DIST).as_posix())  # Lichtkammer-Download nicht ins Zip (zu groß, geht per deploy.sh)
print('fertig:',z)
print(f'Version {VERSION} (Commit {COMMIT})')
if GEAENDERT:
    print('Achtung: Änderungen in src/ oder logos/ sind noch nicht committet. Erst committen, dann neu bauen und hochladen.')
elif SCHON_GETAGGT:
    print(f'Dieser Stand hat schon das Tag web-{VERSION}.')
else:
    print('Nach dem Hochladen den Stand markieren:')
    print(f'  git tag -a web-{VERSION} -m "lurohome {VERSION}" && git push origin web-{VERSION}')
