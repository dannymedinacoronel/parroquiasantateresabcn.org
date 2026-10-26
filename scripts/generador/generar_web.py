import sys, os, re

ROOT = sys.argv[1]

import html as _html
import importlib.util as _ilu
_hs = _ilu.spec_from_file_location("homilias", os.path.join(os.path.dirname(os.path.abspath(__file__)), "homilias.py"))
HOM = _ilu.module_from_spec(_hs); _hs.loader.exec_module(HOM)
HOMILIAS, AUTORES = HOM.load(ROOT)
esc = lambda t: _html.escape(t or "", quote=False)
qesc = lambda t: _html.escape(t or "", quote=True)   # para textos que acaban dentro de un atributo

# Revista digital: el módulo de la portada se edita desde el panel (colección «Revista digital»)
import json as _json
try:
    with open(os.path.join(ROOT, "contenido", "revista.json"), encoding="utf-8") as _fh:
        REVISTA = _json.load(_fh) or {}
except (OSError, ValueError):
    REVISTA = {}
REVISTA_ON = REVISTA.get("mostrar", True) is not False
# Números y artículos de la revista (colecciones «Revista · Números» y «Revista · Artículos» del panel)
_rs = _ilu.spec_from_file_location("revista", os.path.join(os.path.dirname(os.path.abspath(__file__)), "revista.py"))
REV = _ilu.module_from_spec(_rs); _rs.loader.exec_module(REV)
REV_ISSUES = REV.load(ROOT, HOM)
# En Netlify las fotos subidas desde el panel se sirven reducidas (Image CDN); en local, tal cual
ON_NETLIFY = os.environ.get("NETLIFY") == "true"

# Versión de cada archivo común (huella de su contenido): al cambiar el archivo cambia su
# dirección (site.css?v=...) y ningún navegador puede seguir usando una copia antigua.
import hashlib as _hashlib
V = {}
for _f in ("css/fonts.css", "css/site.css", "js/site.js", "js/liturgia.js", "data/avisos.js"):
    with open(os.path.join(ROOT, _f), "rb") as _fh:
        V[_f] = _hashlib.md5(_fh.read()).hexdigest()[:10]

# Menú principal: 5 apartados. Cada subapartado: (texto, enlace, icono pequeño de SAC_ICONS).
# «§» abre un grupo con título; «+» marca contenido propio de la parroquia (con la cruz).
# La clave del apartado admite varias páginas («historia|organigrama») para marcarlo como activo.
NAV = [
    ("portada|buscador", "Inicio", "index.html", [
        ("§", "Bienvenidos", "index.html"),
        ("Quiénes somos", "index.html#bienvenida", "torre"),
        ("Próxima misa y horarios", "index.html#horarios", "reloj"),
        ("Reflexión de la semana", "index.html#reflexion", "libro"),
        ("Cómo llegar", "index.html#ubicacion", "pin"),
        ("Buscar una parroquia", "html/buscador-parroquias.html", "globo"),
        ("¶", "¿Es tu primera visita?", "html/contacto.html#mapa", "Horarios y cómo llegar"),
    ]),
    ("eucaristias", "Celebraciones", "html/misas.html", [
        ("§", "Eucaristía", "html/misas.html"),
        ("Horarios de misa", "html/misas.html#horarios", "reloj"),
        ("Misa con coro góspel", "html/misas.html#gospel", "nota"),
        ("Calendario semanal", "html/misas.html#calendario", "cal"),
        ("¶", "¿Quieres pedir un sacramento?", "html/contacto.html#escribenos", "Escríbenos y te acompañamos"),
        ("§", "Sacramentos", "html/adminsacra.html"),
        ("Bautismo", "html/bautismo.html", "agua"),
        ("Primera Comunión", "html/comuniones.html", "caliz"),
        ("Confirmación", "html/confirmacion.html", "paloma"),
        ("Matrimonio y aniversarios", "html/matrimonio.html", "anillos"),
        ("Perdón", "html/perdon.html", "manos"),
        ("Unción de los enfermos", "html/uncion.html", "oleo"),
    ]),
    ("dinamica", "Comunidad", "html/dinamicapastoral.html", [
        ("§", "Vida de la comunidad", "html/dinamicapastoral.html"),
        ("Grupos y servicios", "html/dinamicapastoral.html", "grupo"),
        ("Jóvenes", "html/jovenes2alternativa.html", "persona"),
        ("Momentos de la comunidad", "html/dinamicapastoral.html#momentos", "foto"),
        ("¶", "¿Quieres colaborar?", "html/contacto.html#escribenos", "Únete a un grupo de la parroquia"),
    ]),
    ("noticias|familia", "Actualidad", "html/noticias.html", [
        ("§parish", "Parroquia", "html/noticias-parroquia.html"),
        ("+Noticias de la parroquia", "html/noticias-parroquia.html"),
        ("+Última reflexión", "__ULTIMA__"),
        ("+Todas las reflexiones", "html/humiliasmenu.html"),
    ] + ([("+Revista digital", "html/revista.html")] if REVISTA_ON or REV_ISSUES else []) + [
        ("§", "Palabra de Dios"),
        ("Evangelio de hoy", "index.html#actualidad", "libro"),
        ("Evangelio para la familia", "html/evangelio-familia.html", "grupo"),
        ("§", "Iglesia"),
        ("Vaticano y Arzobispado", "html/noticias.html#actualidad-iglesia", "globo"),
    ]),
    ("historia|organigrama", "La parroquia", "html/historia.html", [
        ("§", "Historia", "html/historia.html"),
        ("Nuestra historia", "html/historia.html#parroquia", "torre"),
        ("Línea del tiempo", "html/historia.html#linea-del-tiempo", "cal"),
        ("Archivo histórico", "html/historia.html#archivo", "libro"),
        ("Imágenes y vídeos", "html/imagenes.html", "foto"),
        ("§", "Organización", "html/organigramaparroquial.html"),
        ("Organigrama", "html/organigramaparroquial.html#estructura", "persona"),
        ("Consejos parroquiales", "html/organigramaparroquial.html#consejos", "cuentas"),
        ("¶", "¿Guardas fotos antiguas?", "html/contacto.html?motivo=Archivo%20histórico#escribenos", "Compártelas con el archivo"),
    ]),
    ("contacto", "Contacto", "html/contacto.html", [
        ("§", "Estamos para ayudarte", "html/contacto.html"),
        ("Escríbenos", "html/contacto.html#escribenos", "mail"),
        ("Llamar a la parroquia", "tel:+34619040913", "phone"),
        ("Despacho parroquial", "html/adminsacra.html#despacho", "reloj"),
        ("Mapa y cómo llegar", "html/contacto.html#mapa", "pin"),
    ]),
]

if HOMILIAS:
    NAV = [(k, l, p, [(c[0], HOMILIAS[0]["url"]) + tuple(c[2:]) if c[1] == "__ULTIMA__" else c for c in ch]) for k, l, p, ch in NAV]
else:
    NAV = [(k, l, p, [c for c in ch if c[1] != "__ULTIMA__"]) for k, l, p, ch in NAV]

CHEVRON = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>')


PARISH_ICON = ('<svg class="parish-ico" viewBox="0 0 26 34" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round">'
               '<path d="M13 1.5v31M4.5 10.5h17" stroke-width="2.4"/><circle cx="13" cy="10.5" r="3.4" stroke-width="1.6"/></svg>')


def nav_items(depth, active):
    out = []
    for n, (key, label, path, children) in enumerate(NAV):
        cur = active in key.split("|")
        rows, heads = [], 0
        for c in children:
            l, p = c[0], c[1]
            if l.startswith("§"):   # título de grupo dentro del submenú (el segundo abre la otra columna)
                heads += 1
                cls = "sub-heading" + (" parish" if l == "§parish" else "") + (" col-break" if heads == 2 else "")
                if len(c) > 2:   # el título lleva a la página general del grupo (p. ej. Sacramentos)
                    rows.append(f'                    <li class="{cls}"><a href="{href(c[2], depth)}" class="sub-heading-link"><span>{p}</span><small>Ver todo</small></a></li>')
                else:
                    rows.append(f'                    <li class="{cls}">{p}</li>')
            elif l == "¶":  # tarjeta de acción (rellena el hueco de la columna corta)
                rows.append(f'                    <li class="sub-cta"><a href="{href(c[2], depth)}" class="sub-cta-link"><strong>{p}</strong><span>{c[3]}<i aria-hidden="true">&nbsp;&rarr;</i></span></a></li>')
            elif l.startswith("+"):  # contenido propio de la parroquia: con la cruz
                rows.append(f'                    <li class="parish-item"><a href="{href(p, depth)}" class="sub-link parish-link">{PARISH_ICON}<span>{l[1:]}</span></a></li>')
            else:
                ico = SAC_ICONS.get(c[2], "") if len(c) > 2 else ""
                rows.append(f'                    <li><a href="{href(p, depth)}" class="sub-link"><span class="sub-ico">{ico}</span><span>{l}</span></a></li>')
        cols = " cols" if sum(1 for c in children if c[0].startswith("§")) >= 2 else ""
        subs = "\n".join(rows)
        out.append(
            f'            <li class="nav-item has-sub">\n'
            f'                <a href="{href(path, depth)}" class="nav-link{" active" if cur else ""}"{" aria-current=\"page\"" if cur else ""}>{label}</a>\n'
            f'                <button type="button" class="sub-toggle" aria-expanded="false" aria-controls="submenu-{n}" aria-label="{label}: submenú">{CHEVRON}</button>\n'
            f'                <ul class="sub-menu{cols}" id="submenu-{n}">\n{subs}\n                </ul>\n'
            f'            </li>')
    return "\n".join(out)

PARROQUIA_LINKS = [
    ("Eucaristías y calendario", "html/misas.html"),
    ("Sacramentos", "html/adminsacra.html"),
    ("Catequesis", "html/catequesis.html"),
    ("Homilías", "html/humiliasmenu.html"),
    ("Jóvenes", "html/jovenes2alternativa.html"),
    ("Imágenes y vídeos", "html/imagenes.html"),
]


SITE = "https://parroquiasantateresabcn.netlify.app/"

# Contacto de la parroquia
EMAIL = "albertsols@gmail.com"
TEL = "+34619040913"            # para el enlace tel: (se puede pulsar para llamar)
TEL_TXT = "+34 619 040 913"     # tal como se muestra
# Formularios (contacto y Primera Comunión): se envían por correo a EMAIL a través de FormSubmit.
# La primera vez que alguien envía uno, FormSubmit manda a ese correo un mensaje para ACTIVARLO.
# Código que FormSubmit asigna a albertsols@gmail.com (así la dirección no aparece en el código de la web)
FORM_ALIAS = "2823149fadce475f74b32bfd2b23cd79"
FORM_MAIL = "https://formsubmit.co/" + FORM_ALIAS

# Datos del titular para Aviso legal y Privacidad.
# Los marcados como PENDIENTE deben completarse con los datos reales de la parroquia.
LEGAL = {
    "titular": "Parroquia de Santa Teresa de Jesús (Arzobispado de Barcelona)",
    "domicilio": "Carrer del Llobregós, 132, 08032 Barcelona",
    "email": "albertsols@gmail.com",
    "dpd": 'El designado por el Arzobispado de Barcelona, a través de <a href="https://esglesia.barcelona/es/" target="_blank" rel="noopener">esglesia.barcelona</a>',
    # Si se conoce el NIF de la parroquia, añadir aquí "nif" y su línea en el Aviso legal y la Privacidad.
    "actualizado": "20 de octubre de 2026",
}

CTA_BAND = """
        <section class="cta-band">
            <div>
                <span class="subtitulo text-left">Estamos para ayudarte</span>
                <h2 class="text-left">¿Tienes alguna pregunta?</h2>
                <p>Escríbenos o pásate por el despacho parroquial: los viernes por la tarde, y antes o después de cada misa.</p>
            </div>
            <div class="btn-group">
                <a href="contacto.html" class="btn btn-solid">Contactar</a>
                <a href="https://goo.gl/maps/Y4SiUkiMGwp" class="btn" target="_blank" rel="noopener">Cómo llegar</a>
            </div>
        </section>
"""

LOGO_MARK = ('<svg class="logo-mark" viewBox="0 0 26 34" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round">'
             '<path d="M13 1.5v31M4.5 10.5h17" stroke-width="2"/><circle cx="13" cy="10.5" r="3.4" stroke-width="1.3"/></svg>')

# Fotos optimizadas (fotosdefinitivas/web). Las que no están aquí se usan tal cual.
WEB = {"DSC_0448.JPG", "DSC_0568.JPG", "IMG_5471.jpg", "IMG_5495.jpg", "caritas.jpg", "catequesis.png",
       "familia.jpg", "rezando.jpg", "equipoespiritualidad.jpeg", "limpieza.jpg", "salidas.png", "santateresa.jpg",
       "colegio.jpeg", "vidacreixent.jpg", "DSC_0586.JPG", "albertsols.png", "magdalena.jpg", "humiliasmenu1.JPG", "nuevalife.jpeg",
       "mercadet.jpg"}


def img(name, depth=1):
    p = "../" * depth + "fotosdefinitivas/"
    if name in WEB:
        return p + "web/" + os.path.splitext(name)[0].lower() + ".jpg"
    return p + name


def href(path, depth):
    """Ruta relativa desde la raíz (depth 0) o desde /html (depth 1)."""
    if path.startswith(("tel:", "mailto:", "http")):
        return path
    if depth == 0:
        if path.startswith("index.html#"):
            return path[len("index.html"):]
        return path
    if depth == 1:
        if path.startswith("html/"):
            return path[5:]
        return "../" + path
    # depth 2: páginas de html/reflexiones/
    import posixpath as _pp
    target, _, anchor = path.partition("#")
    rel = _pp.relpath(target, "html/reflexiones")
    return rel + ("#" + anchor if anchor else "")


def page(depth, title, desc, body, active=None, extra_head="", extra_scripts="", full_title=None, cta=None):
    p = "../" * depth
    nav = nav_items(depth, active)
    parroquia = "\n".join(
        '                    <li><a href="%s">%s</a></li>' % (href(path, depth), label)
        for label, path in PARROQUIA_LINKS)
    logo_href = "#" if depth == 0 else "../" * depth + "index.html"
    if cta is None:
        cta = depth == 1 and active != "contacto"
    cta_html = CTA_BAND if cta else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="VPnsEJ8eoLn1oCmTMKtjPE2oXmyNlapYjslb4OXHVe8" />
    <title>{full_title or (title + " | Parroquia Santa Teresa de Jesús")}</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="__URL__">
__HREFLANG__
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Parroquia Santa Teresa de Jesús">
    <meta property="og:title" content="{full_title or (title + " | Parroquia Santa Teresa de Jesús")}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="__URL__">
    <meta property="og:image" content="{SITE}fotosdefinitivas/web/portada3.jpg">
    <meta property="og:locale" content="__LOCALE__">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" href="{p}favicon.svg?v=3" type="image/svg+xml">
    <link rel="icon" href="{p}favicon-48.png?v=3" sizes="48x48" type="image/png">
    <link rel="apple-touch-icon" href="{p}apple-touch-icon.png?v=3">
    <link rel="manifest" href="{p}site.webmanifest">

    <link rel="stylesheet" href="{p}css/fonts.css?v={V["css/fonts.css"]}">
    <link rel="stylesheet" href="{p}css/site.css?v={V["css/site.css"]}">
    <meta name="theme-color" content="#bfa065">
    <script>document.documentElement.classList.add("js");</script>
    <script type="speculationrules">{{"prerender":[{{"where":{{"selector_matches":"a[hreflang]"}},"eagerness":"moderate"}}],"prefetch":[{{"where":{{"and":[{{"href_matches":"/*"}},{{"not":{{"href_matches":"/admin/*"}}}},{{"not":{{"selector_matches":"a[hreflang]"}}}}]}},"eagerness":"moderate"}}]}}</script>
{extra_head}</head>
<body>
    <a class="skip-link" href="#contenido">Saltar al contenido</a>

    <header>
        <a href="{logo_href}" class="logo">{LOGO_MARK}<span>Parroquia Santa Teresa<br>de Jesús</span></a>

        <button class="hamburger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="menu-principal">
            <span class="bar"></span><span class="bar"></span><span class="bar"></span>
        </button>

        <nav aria-label="Menú principal">
            <ul class="nav-menu" id="menu-principal">
{nav}
__MENU_EXTRA__            </ul>
        </nav>
__LANGSWITCH__    </header>

    <main id="contenido">
{body}{cta_html}
    </main>

    <footer>
        <div class="footer-brand">
            {LOGO_MARK}
            <strong>Santa Teresa de Jesús</strong>
            <span>Parroquia · El Carmel · Barcelona</span>
        </div>
        <div class="footer-grid">
            <div class="footer-col">
                <h4>Santa Teresa de Jesús</h4>
                <p>Carrer del Llobregós, 132</p>
                <p>08032 Barcelona</p>
                <a href="https://goo.gl/maps/Y4SiUkiMGwp" class="footer-map" target="_blank" rel="noopener">Ver en Google Maps &rarr;</a>
            </div>

            <div class="footer-col">
                <h4>La Parroquia</h4>
                <ul class="footer-links">
{parroquia}
                </ul>
            </div>

            <div class="footer-col">
                <h4>Enlaces de Interés</h4>
                <ul class="footer-links">
                    <li><a href="https://esglesia.barcelona/es/" target="_blank" rel="noopener">Arzobispado de Barcelona</a></li>
                    <li><a href="https://caritas.barcelona" target="_blank" rel="noopener">Cáritas Barcelona</a></li>
                    <li><a href="{href('html/buscador-parroquias.html', depth)}">Buscador de Parroquias</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Contacto</h4>
                <ul class="footer-links">
                    <li><a href="{href('html/contacto.html', depth)}">Contactar</a></li>
                    <li><a href="tel:{TEL}">Llamar: {TEL_TXT}</a></li>
                    <li><a href="https://www.instagram.com/p.santateresadejesusbcn/" target="_blank" rel="noopener">Instagram</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; <span class="js-year">2026</span> Parroquia Santa Teresa de Jesús. Carrer del Llobregós, 132 · Barcelona</span>
            <nav class="legal-links" aria-label="Información legal">
                <a href="{href('html/aviso-legal.html', depth)}">Aviso legal</a>
                <a href="{href('html/privacidad.html', depth)}">Privacidad</a>
                <a href="{href('html/cookies.html', depth)}">Cookies</a>
                <button type="button" class="link-button" data-cookie-settings>Configurar cookies</button>
                <a href="#">Volver arriba &uarr;</a>
            </nav>
        </div>
    </footer>
{ultima_template(depth)}
    <script src="{p}data/avisos.js?v={V["data/avisos.js"]}"></script>
    <script src="{p}js/site.js?v={V["js/site.js"]}"></script>
{extra_scripts}
</body>
</html>
"""


def page_hero(subtitle, title, photo="web/portada3.jpg", crumb=None, pos="center 30%"):
    url = "../fotosdefinitivas/" + photo
    return f"""        <section class="page-hero" style="background-image:url('{url}'); background-position:{pos}">
            <span class="eyebrow">{subtitle}</span>
            <h1>{title}</h1>
            <div class="hero-divider"></div>
            <nav class="breadcrumb" aria-label="Ruta"><a href="../index.html">Inicio</a><span>/</span>{crumb or title}</nav>
        </section>
"""


def cincopa(widget_id, fid):
    return f"""<div class="consent-embed" data-service="Cincopa (galería de fotos)"><div id="cp_widget_{widget_id}">...</div>
                <script type="text/plain" data-consent="embeds">
                    var cpo = []; cpo["_object"] = "cp_widget_{widget_id}"; cpo["_fid"] = "{fid}";
                    var _cpmp = _cpmp || []; _cpmp.push(cpo);
                    (function() {{ var cp = document.createElement("script"); cp.type = "text/javascript";
                    cp.async = true; cp.src = "//www.cincopa.com/media-platform/runtime/libasync.js";
                    var c = document.getElementsByTagName("script")[0];
                    c.parentNode.insertBefore(cp, c); }})();
                </script></div>"""


PAGES = {}


ORNAMENT = ('<svg class="ornament" viewBox="0 0 120 24" fill="none" stroke="currentColor" aria-hidden="true">'
            '<path d="M0 12h44M76 12h44" stroke-width="1"/><path d="M60 3v18M53 9.5h14" stroke-width="1.4" stroke-linecap="round"/>'
            '<path d="M44 12l4-3 4 3-4 3z" stroke-width="1"/><path d="M68 12l4-3 4 3-4 3z" stroke-width="1"/></svg>')

SAC_ICONS = {
    "agua": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/><path d="M9 14.5a3 3 0 0 0 3 3"/></svg>',
    "paloma": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 13c3 0 5-1 7-3l4-4c1.5-1.5 4-1 5 0l2 1-2 1c0 4-3 8-8 8H7l-3 3v-3"/><path d="M10 10c-1-2-1-4 0-6 2 1 3 3 3 5"/><circle cx="17" cy="7" r=".6" fill="currentColor"/></svg>',
    "anillos": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><circle cx="9" cy="14" r="5.5"/><circle cx="15" cy="14" r="5.5"/><path d="M10.5 4.5l1.5-2 1.5 2-1.5 1.5z" stroke-linejoin="round"/></svg>',
    "manos": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21V11M12 11c0-3-1.5-6-4-8-.5 3 0 6 4 8zM12 11c0-3 1.5-6 4-8 .5 3 0 6-4 8z"/><path d="M5 14c2 0 4 1.5 7 4 3-2.5 5-4 7-4"/></svg>',
}


SAC_ICONS.update({
    "nota": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    "foto": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="6.5" width="18" height="13" rx="2"/><circle cx="12" cy="13" r="3.5"/><path d="M8.5 6.5l1.5-2h4l1.5 2"/></svg>',
    "torre": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v4M10 4h4M7 21V11l5-4 5 4v10M4 21h16M10 21v-3.5a2 2 0 0 1 4 0V21"/></svg>',
    "globo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.5 3.5 5.5 3.5 8.5s-1 6-3.5 8.5c-2.5-2.5-3.5-5.5-3.5-8.5s1-6 3.5-8.5z"/></svg>',
    # Unción de los enfermos: frasco del óleo con la cruz
    "oleo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.5 2.5h5M10.2 2.5v3.6L7 10v8.6A2.4 2.4 0 0 0 9.4 21h5.2a2.4 2.4 0 0 0 2.4-2.4V10l-3.2-3.9V2.5"/><path d="M12 11.5v6M9.6 13.8h4.8"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="1.5"/><path d="M3.5 6.5l8.5 7 8.5-7"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" aria-hidden="true"><path d="M5 3.5h3.2l1.6 4.2-2.1 1.4a11 11 0 0 0 5.2 5.2l1.4-2.1 4.2 1.6V17a2.5 2.5 0 0 1-2.5 2.5A15.5 15.5 0 0 1 2.5 6 2.5 2.5 0 0 1 5 3.5z"/></svg>',
    "reloj": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    "insta": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".8" fill="currentColor"/></svg>',
    "libro": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" aria-hidden="true"><path d="M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5z"/><path d="M12 6.5v13"/></svg>',
    "caliz": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3.5h12c0 5-2.7 8-6 8s-6-3-6-8z"/><path d="M12 11.5V19M8 20.5h8"/><circle cx="12" cy="6.5" r="1.4"/></svg>',
    "persona": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/><path d="M12 1.5v2"/></svg>',
    "grupo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="3"/><circle cx="5" cy="10" r="2.2"/><circle cx="19" cy="10" r="2.2"/><path d="M7 19.5c0-2.8 2.2-5 5-5s5 2.2 5 5M1.5 18c0-2.2 1.6-3.8 3.5-3.8M22.5 18c0-2.2-1.6-3.8-3.5-3.8"/></svg>',
    "cuentas": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4.5" y="3" width="15" height="18" rx="1.5"/><path d="M8 7.5h8M8 11.5h2M12 11.5h2M8 15h2M12 15h2M16 11.5v3.5"/></svg>',
})


def info_card(icon, label, value):
    return f"""                <div class="info-card">
                    <div class="icon-circle">{SAC_ICONS[icon]}</div>
                    <strong>{label}</strong>
                    <span>{value}</span>
                </div>"""


def news_columns(limit, depth):
    p = "../" * depth
    return f"""            <div class="news-grid">
                <div class="news-col">
                    <div class="news-source"><span class="news-badge vatican">Santa Sede</span><h3>Vaticano</h3><a href="https://www.vaticannews.va/es.html" target="_blank" rel="noopener">vaticannews.va &rarr;</a></div>
                    <div class="news-list" data-news="vaticano" data-limit="{limit}"><p class="news-empty">Cargando noticias…</p></div>
                </div>
                <div class="news-col">
                    <div class="news-source"><span class="news-badge diocese">Diócesis</span><h3>Arzobispado de Barcelona</h3><a href="https://esglesia.barcelona/es/" target="_blank" rel="noopener">esglesia.barcelona &rarr;</a></div>
                    <div class="news-list" data-news="arzobispado" data-limit="{limit}"><p class="news-empty">Cargando noticias…</p></div>
                </div>
            </div>
            <p class="news-updated" data-news-updated></p>"""


NEWS_HEAD_0 = '    <script src="data/noticias.js"></script>\n'
NEWS_HEAD_1 = '    <script src="../data/noticias.js"></script>\n'


# Unción de los enfermos: el mismo texto en la portada y en Sacramentos
UNCION_TXT = "Para enfermos y personas mayores, en casa, en el hospital o en la residencia. Si es urgente, llamad a la parroquia."


def icon_card(icon, title, text, link, cta=None, aid=None):
    more = f'\n                    <span class="icon-card-cta">{cta} &rarr;</span>' if cta else ""
    anchor = f' id="{aid}"' if aid else ""
    return f"""                <a class="icon-card"{anchor} href="{link}">
                    <div class="icon-circle">{SAC_ICONS[icon]}</div>
                    <h3>{title}</h3>
                    <p>{text}</p>{more}
                </a>"""


def mosaic(photos, depth):
    """photos: lista de (archivo en web/, texto alternativo, clase opcional)."""
    p = "../" * depth + "fotosdefinitivas/web/"
    items = []
    for name, alt, cls in photos:
        c = f' class="{cls}"' if cls else ""
        items.append(f'                <a href="{p}{name}"{c}><img src="{p}{name}" alt="{alt}" loading="lazy"></a>')
    return '            <div class="mosaic">\n' + "\n".join(items) + "\n            </div>"


GALLERY = [
    ("dsc_0541.jpg", "Interior de la iglesia durante la eucaristía", "wide"),
    ("img_5432.jpg", "Música en la eucaristía", "tall"),
    ("salidas.jpg", "Salida parroquial con Mn. Albert Sols", ""),
    ("dsc_0589.jpg", "Bendición de ramos en el Domingo de Ramos", ""),
    ("dsc_0599webog.jpg", "El campanario durante el Domingo de Ramos", "tall"),
    ("fotobodapepi.jpg", "Celebración de un aniversario de boda", ""),
    ("img_5434.jpg", "Celebración de la eucaristía", ""),
    ("dsc_0512.jpg", "La comunidad reunida en la iglesia", "wide"),
]

# Galería «Momentos de la comunidad» (Dinámica Pastoral): salidas, celebraciones y vida parroquial
MOMENTOS = [
    ("salidas.jpg", "Salida parroquial con Mn. Albert Sols", "wide"),
    ("fotobodapepi.jpg", "Celebración de un aniversario de boda", "tall"),
    ("dsc_0591.jpg", "Bendición de los ramos en el patio", ""),
    ("img_5495.jpg", "Encuentro en la capilla", ""),
    ("dsc_0546.jpg", "La iglesia llena durante una celebración", "wide"),
    ("dsc_0586.jpg", "Domingo de Ramos con toda la comunidad", ""),
    ("img_5432.jpg", "Música en la eucaristía", "tall"),
    ("mercadet.jpg", "La parroquia, en el corazón del Carmel", ""),
    ("dsc_0541.jpg", "Eucaristía dominical", ""),
    ("dsc_0599webog.jpg", "El campanario en fiesta", ""),
]

# Vista de Instagram propia: fotos de la parroquia en cuadrícula, cada una lleva al perfil.
# (Antes era un widget de Elfsight; su plan gratuito se queda sin visitas cada mes y el recuadro salía vacío.)
IG_URL = "https://www.instagram.com/p.santateresadejesusbcn/"
ICON_IG = ('<svg class="ig-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
           '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1" fill="currentColor" stroke="none"/></svg>')
IG_PHOTOS = [
    ("dsc_0589.jpg", "Bendición de ramos en el Domingo de Ramos"),
    ("salidas.jpg", "Salida parroquial con Mn. Albert Sols"),
    ("img_5432.jpg", "Música en la eucaristía"),
    ("fotobodapepi.jpg", "Celebración de un aniversario de boda"),
    ("dsc_0541.jpg", "Eucaristía dominical"),
    ("dsc_0599webog.jpg", "El campanario en fiesta"),
    ("img_5495.jpg", "Encuentro en la capilla"),
    ("dsc_0546.jpg", "La iglesia llena durante una celebración"),
    ("mercadet.jpg", "La parroquia, en el corazón del Carmel"),
]


def ig_grid(depth):
    pre = "../" * depth + "fotosdefinitivas/web/"
    tiles = "\n".join(f'''                <a class="ig-tile" href="{IG_URL}" target="_blank" rel="noopener"><img src="{pre}{f}" alt="{alt}" loading="lazy" decoding="async"></a>''' for f, alt in IG_PHOTOS)
    return f'''<div class="ig-grid">
{tiles}
            </div>'''


def ig_profile(depth, cls=""):
    return f'''<div class="ig-phone-top {cls}">
                        <img src="{"../" * depth}fotosdefinitivas/web/santateresa-retrato.jpg" alt="" loading="lazy">
                        <div><strong>p.santateresadejesusbcn</strong><span>Parroquia Santa Teresa de Jesús · Barcelona</span></div>
                        <a href="{IG_URL}" target="_blank" rel="noopener">Seguir</a>
                    </div>'''


# ---------------------------------------------------------------- REVISTA DIGITAL
# Recuadro de la portada (contenido/revista.json, panel → «Revista · Recuadro de la portada»):
#   sin números publicados → «Próximamente» con el texto del recuadro
#   con números publicados → el último número, con su portada y enlace a leerlo
# Números y artículos (panel → «Revista · Números» y «Revista · Artículos») generan:
#   html/revista.html                       último número y archivo de todos
#   html/revista/<número>.html              presentación, PDF y artículos de un número
#   html/revista/<número>--<artículo>.html  cada artículo
def _paragraphs(text):
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def _media(path, depth):
    """Ruta guardada por el panel («/fotosdefinitivas/...» o «fotosdefinitivas/...») → relativa a la página."""
    path = (path or "").strip()
    if not path or re.match(r"^(https?:)?//", path):
        return path
    return "../" * depth + path.lstrip("/")


def rev_img(path, depth, width, alt="", cls="", lazy=True):
    """Foto subida desde el panel. En Netlify se sirve reducida al ancho necesario (Image CDN) y,
    si eso fallara, el navegador carga el original."""
    if not path:
        return ""
    attrs = (f' class="{cls}"' if cls else "") + (' loading="lazy"' if lazy else "") + ' decoding="async"'
    if ON_NETLIFY and not re.match(r"^(https?:)?//", path):
        from urllib.parse import quote
        original = "/" + path.lstrip("/")
        src = f"/.netlify/images?url={quote(original)}&amp;w={width}&amp;q=78"
        return f'<img src="{src}" alt="{esc(alt)}"{attrs} onerror="this.onerror=null;this.src=\'{original}\'">'
    return f'<img src="{_media(path, depth)}" alt="{esc(alt)}"{attrs}>'


REV_DEFAULT_COVER = "fotosdefinitivas/web/dsc_0546.jpg"


def rev_label(n):
    return f"Número {n['num']}" if n.get("num") else ""


def rev_cover(depth, img="", label="", ribbon="", complete=False, link=""):
    """Portada de revista dibujada. Si la imagen ya es la portada completa, se muestra tal cual."""
    if complete and img:
        inner = rev_img(img, depth, 640)
        cls = "revista-cover is-complete"
    else:
        inner = (rev_img(img or REV_DEFAULT_COVER, depth, 640)
                 + f'\n                        <div class="revista-mast">{LOGO_MARK}<strong>Santa Teresa</strong><small>Revista digital de la parroquia</small></div>'
                 + (f'\n                        <span class="revista-issue">{esc(label)}</span>' if label else ""))
        cls = "revista-cover"
    tag, attr = ("a", f' href="{link}" aria-label="Abrir la revista"') if link else ("div", "")
    rib = f'\n                    <span class="revista-ribbon">{ribbon}</span>' if ribbon else ""
    return f"""<div class="revista-cover-wrap">
                    <{tag} class="{cls}"{attr}>
                        {inner}
                    </{tag}>{rib}
                </div>"""


def rev_is_new(n, days=45):
    from datetime import date as _date
    try:
        return 0 <= (_date.today() - _date.fromisoformat(n["fecha"])).days <= days
    except (KeyError, ValueError):
        return False


def rev_buttons(n, depth, here=""):
    """Botones de un número: leerlo en la web y, si los tiene, el PDF y el enlace externo."""
    root = "../" * depth
    out = []
    if here != "numero":
        out.append(f'<a class="btn btn-solid" href="{root}{n["url"]}">Leer la revista &rarr;</a>')
    if n["pdf"]:
        out.append(f'<a class="btn{" btn-solid" if here == "numero" else ""}" href="{_media(n["pdf"], depth)}" target="_blank" rel="noopener">Leer en PDF</a>')
    if n["enlace"]:
        out.append(f'<a class="btn" href="{esc(n["enlace"])}" target="_blank" rel="noopener">Ver la revista en línea</a>')
    return "\n                        ".join(out)


def revista_module(depth, in_archive=False):
    """Recuadro de la portada (y cabecera de la página de la revista)."""
    r = REVISTA
    if not REVISTA_ON and not REV_ISSUES:
        return ""
    if REV_ISSUES:
        n = REV_ISSUES[0]
        root = "../" * depth
        arts = n["articulos"][:4]
        toc = ""
        if arts:
            items = "".join(f'\n                        <li><a href="{root}{a["url"]}">{esc(a["titulo"])}</a></li>' for a in arts)
            toc = f"""
                    <p class="revista-toc-title">En este número</p>
                    <ul class="revista-toc">{items}
                    </ul>"""
        more = f'\n                        <a class="btn" href="{root}html/revista.html">Todos los números</a>' if len(REV_ISSUES) > 1 and not in_archive else ""
        kicker = "Revista digital" + (f" · {rev_label(n)}" if n.get("num") else "")
        return f"""
        <section id="revista" class="revista">
            <div class="revista-grid">
                {rev_cover(depth, n["portada"], rev_label(n), "Nuevo número" if rev_is_new(n) else "", n.get("portada_completa") is True, root + n["url"])}
                <div class="revista-body">
                    <span class="subtitulo text-left">{kicker}</span>
                    <h2 class="text-left">{esc(n["titulo"])}</h2>
                    <hr class="section-divider left">
                    {f'<p class="lead">{esc(n["extracto"])}</p>' if n["extracto"] else ""}{toc}
                    <div class="btn-group">
                        {rev_buttons(n, depth)}{more}
                    </div>
                </div>
            </div>
        </section>
"""
    pars = "".join(f'\n                    <p class="lead">{esc(p)}</p>' for p in _paragraphs(r.get("texto")))
    return f"""
        <section id="revista" class="revista is-soon">
            <div class="revista-grid">
                {rev_cover(depth, (r.get("portada") or "").lstrip("/"), r.get("numero") or "", "Próximamente")}
                <div class="revista-body">
                    <span class="subtitulo text-left">Revista digital</span>
                    <h2 class="text-left">{esc(r.get("titulo") or "Revista digital de la Parroquia")}</h2>
                    <hr class="section-divider left">{pars}
                    <div class="btn-group">
                        <span class="btn btn-solid is-soon" aria-disabled="true">Próximamente disponible</span>
                        <a class="btn" href="{IG_URL}" target="_blank" rel="noopener">Te avisaremos en Instagram</a>
                    </div>
                </div>
            </div>
        </section>
"""


def rev_issue_card(n, depth):
    root = "../" * depth
    return f"""
                <a class="rv-issue" href="{root}{n["url"]}">
                    <span class="rv-issue-cover{' is-complete' if n.get('portada_completa') is True and n['portada'] else ''}">{rev_img(n["portada"] or REV_DEFAULT_COVER, depth, 420)}</span>
                    <span class="rv-issue-num">{esc(rev_label(n))}</span>
                    <strong>{esc(n["titulo"])}</strong>
                    {date_long(n, "rv-issue-date")}
                </a>"""


def rev_article_card(a, depth):
    root = "../" * depth
    thumb = rev_img(a["foto"], depth, 520) if a["foto"] else f'<span class="rv-card-mark">{LOGO_MARK}</span>'
    return f"""
                <a class="rv-card" href="{root}{a["url"]}">
                    <span class="rv-card-img{'' if a["foto"] else ' is-empty'}">{thumb}</span>
                    <span class="rv-card-body">
                        {f'<span class="book-kicker">{esc(a["seccion"])}</span>' if a.get("seccion") else ""}
                        <strong>{esc(a["titulo"])}</strong>
                        {f'<span class="rv-card-text">{esc(a["extracto"])}</span>' if a["extracto"] else ""}
                        {f'<span class="rv-card-author">{esc(a["autor"])}</span>' if a.get("autor") else ""}
                    </span>
                </a>"""


def _hero2(eyebrow, title, crumb, photo="web/dsc_0546.jpg"):
    """Cabecera para las páginas de html/revista/ (una carpeta más abajo)."""
    return (page_hero(eyebrow, title, photo, crumb)
            .replace('href="../index.html"', 'href="../../index.html"')
            .replace("url('../fotosdefinitivas/", "url('../../fotosdefinitivas/"))


def rev_og(html, path):
    """Imagen al compartir la página (WhatsApp, redes): la portada o la foto del artículo."""
    return html.replace(f'content="{SITE}fotosdefinitivas/web/portada3.jpg"', f'content="{SITE}{path}"', 1) if path else html


def revista_archive_page():
    if not REV_ISSUES:
        body = page_hero("Parroquia Santa Teresa de Jesús", "Revista digital", "web/dsc_0546.jpg") + revista_module(1)
        return page(1, "Revista digital", "La revista digital de la Parroquia Santa Teresa de Jesús de Barcelona.", body=body, active="noticias")
    latest, rest = REV_ISSUES[0], REV_ISSUES[1:]
    grid = ""
    if rest:
        grid = f"""
        <section class="section-alt">
            <div class="section-head">
                <span class="subtitulo">Archivo</span>
                <h2>Números anteriores</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="rv-issues">{"".join(rev_issue_card(n, 1) for n in rest)}
            </div>
        </section>
"""
    body = page_hero("Parroquia Santa Teresa de Jesús", "Revista digital", "web/dsc_0546.jpg") + revista_module(1, in_archive=True) + grid
    return rev_og(page(1, "Revista digital", "La revista digital de la Parroquia Santa Teresa de Jesús de Barcelona: todos sus números.", body=body, active="noticias"), latest["portada"])


def revista_issue_page(i, n):
    arts = n["articulos"]
    cards = ""
    if arts:
        cards = f"""
        <section class="section-alt" id="articulos">
            <div class="section-head">
                <span class="subtitulo">{esc(rev_label(n) or "Revista digital")}</span>
                <h2>En este número</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="rv-cards">{"".join(rev_article_card(a, 2) for a in arts)}
            </div>
        </section>
"""
    btns = rev_buttons(n, 2, here="numero")
    others = [o for o in REV_ISSUES if o is not n][:3]
    more = ""
    if others:
        more = f"""
        <section>
            <div class="section-head">
                <span class="subtitulo">Archivo</span>
                <h2>Otros números</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="rv-issues">{"".join(rev_issue_card(o, 2) for o in others)}
            </div>
            <div class="btn-group center" style="margin-top:2.5rem;"><a class="btn" href="../revista.html">Todos los números</a></div>
        </section>
"""
    body = _hero2("Revista digital" + (f" · {rev_label(n)}" if n.get("num") else ""), esc(n["titulo"]), "Revista digital") + f"""
        <section class="revista rv-issue-intro">
            <div class="revista-grid">
                {rev_cover(2, n["portada"], rev_label(n), "", n.get("portada_completa") is True)}
                <div class="revista-body">
                    <span class="subtitulo text-left">{date_long(n)}</span>
                    <h2 class="text-left">{esc(n["titulo"])}</h2>
                    <hr class="section-divider left">
                    <div class="prose rv-presentacion">
{HOM.markdown(n.get("presentacion", "")).replace(' class="illuminated"', "", 1)}
                    </div>
                    <div class="btn-group">
                        {btns}{'<a class="btn" href="#articulos">Ver los artículos</a>' if arts and not btns else ''}
                    </div>
                </div>
            </div>
        </section>
""" + cards + more
    desc = f"{n['titulo']} — revista digital de la Parroquia Santa Teresa de Jesús."
    return rev_og(page(2, qesc(n["titulo"]) + " · Revista digital", qesc(desc), body=body, active="noticias"), n["portada"])


def revista_article_page(n, j, a):
    arts = n["articulos"]
    prev_a = arts[j - 1] if j > 0 else None
    next_a = arts[j + 1] if j + 1 < len(arts) else None

    def nav_card(o, label):
        thumb = rev_img(o["foto"], 2, 200) if o["foto"] else LOGO_MARK
        return f"""
                    <a class="reading-next rv-next" href="{n["slug"]}--{o["slug"]}.html">
                        <span class="rv-next-img">{thumb}</span>
                        <div class="reading-next-text"><span class="book-kicker">{label}</span><strong>{esc(o["titulo"])}</strong>{f'<p>{esc(o["autor"])}</p>' if o.get("autor") else ""}</div>
                        <span class="reading-arrow" aria-hidden="true">&rarr;</span>
                    </a>"""
    cards = (nav_card(next_a, "Siguiente artículo") if next_a else "") + (nav_card(prev_a, "Artículo anterior") if prev_a else "")
    figure = ""
    if a["foto"]:
        cap = f"\n                        <figcaption>{esc(a['pie'])}</figcaption>" if (a.get("pie") or "").strip() else ""
        figure = f"""
                    <figure class="rv-figure">
                        {rev_img(a["foto"], 2, 1100, a.get("pie") or a["titulo"], lazy=False)}{cap}
                    </figure>"""
    entradilla = f'\n                    <p class="lead rv-lead">{esc(a["entradilla"])}</p>' if (a.get("entradilla") or "").strip() else ""
    firma = f'\n                    <p class="firma">{esc(a["autor"])}</p>' if (a.get("autor") or "").strip() else ""
    body = _hero2(esc(a.get("seccion") or n["titulo"]), esc(a["titulo"]), "Revista digital") + f"""
        <section class="reading">
            <div class="reading-wrap">
                <a class="rv-back" href="{n["slug"]}.html">&larr; <span>{esc(rev_label(n) + " · " if n.get("num") else "")}{esc(n["titulo"])}</span></a>
                <article class="prose book-page reading-book rv-article">
                    <div class="reading-head">
                        <span class="book-kicker">{esc(a.get("seccion") or "Revista digital")}</span>
                        <span class="rv-issue-tag">{esc(rev_label(n) or n["titulo"])}</span>
                    </div>
                    <h2 class="reading-title">{esc(a["titulo"])}</h2>
                    {ORNAMENT}{entradilla}{figure}
{HOM.markdown(a.get("texto", ""))}{firma}
                </article>
                <nav class="reading-nav" aria-label="Otros artículos">
                    {'<span class="subtitulo">Sigue leyendo</span>' if cards else ''}{cards}
                    <a class="link-arrow" href="{n["slug"]}.html">Volver al índice del número <span>&rarr;</span></a>
                </nav>
            </div>
        </section>
"""
    desc = a["extracto"][:180] if a["extracto"] else f"{a['titulo']} — revista digital de la Parroquia Santa Teresa de Jesús."
    return rev_og(page(2, qesc(a["titulo"]), qesc(desc), body=body, active="noticias"), a["foto"] or n["portada"])


# Mapa de la portada (el mismo de la página de contacto) y ruta en Google Maps
MAP_EMBED = ("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d11966.759774653801!2d2.1558072908873487!3d41.42424881242464"
             "!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12a4bd4d9ae3237b%3A0xd805a433a983f974"
             "!2sParr%C3%B2quia+Santa+Teresa+de+Jes%C3%BAs!5e0!3m2!1sca!2ses!4v1555520866181!5m2!1sca!2ses")
MAP_DIRECTIONS = ("https://www.google.com/maps/dir/?api=1&amp;destination="
                  "Parr%C3%B2quia+Santa+Teresa+de+Jes%C3%BAs%2C+Carrer+del+Llobreg%C3%B3s+132%2C+08032+Barcelona")
_SVG = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
ICON_PIN = _SVG + '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
ICON_METRO = _SVG + '<rect x="5" y="3" width="14" height="14" rx="3"/><path d="M8 21l2-4M16 21l-2-4M5 11h14"/><circle cx="9" cy="14" r=".6" fill="currentColor"/><circle cx="15" cy="14" r=".6" fill="currentColor"/></svg>'
ICON_CLOCK = _SVG + '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
ICON_PHONE = _SVG + '<path d="M5 3.5h3.2l1.6 4.2-2.1 1.4a11 11 0 0 0 5.2 5.2l1.4-2.1 4.2 1.6V17a2.5 2.5 0 0 1-2.5 2.5A15.5 15.5 0 0 1 2.5 6 2.5 2.5 0 0 1 5 3.5z"/></svg>'

def location_block(big=False, sid="ubicacion"):
    """Mapa a todo lo ancho con la tarjeta «Cómo llegar» (portada y, más grande, Contacto)."""
    return f"""
        <section id="{sid}" class="location{" location-big" if big else ""}">
            <div class="location-map">
                <iframe title="Mapa de la Parroquia Santa Teresa de Jesús" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade"
                    src="{MAP_EMBED}"></iframe>
            </div>
            <div class="location-card">
                <span class="subtitulo">¿Dónde estamos?</span>
                <h2>Cómo llegar</h2>
                <hr class="section-divider left">
                <ul class="location-list">
                    <li>
                        {ICON_PIN}
                        <div><strong>Carrer del Llobregós, 132</strong><span>08032 Barcelona · barrio de El Carmel</span></div>
                    </li>
                    <li>
                        {ICON_METRO}
                        <div><strong>Metro L5 · El Carmel</strong><span>La parada más cercana, a pocos minutos a pie</span></div>
                    </li>
                    <li>
                        {ICON_CLOCK}
                        <div><strong>Misas</strong><span>Laborables y sábados 19:00 h · Domingos 11:00 y 13:15 h</span></div>
                    </li>
                    <li>
                        {ICON_PHONE}
                        <div><strong><a class="tel-link" href="tel:{TEL}">{TEL_TXT}</a></strong><span>Pulsa para llamar a la parroquia</span></div>
                    </li>
                </ul>
                <div class="btn-group">
                    <a class="btn btn-solid" href="{MAP_DIRECTIONS}" target="_blank" rel="noopener">Cómo llegar</a>
                    <a class="btn" href="https://goo.gl/maps/Y4SiUkiMGwp" target="_blank" rel="noopener">Abrir en Google Maps</a>
                </div>
            </div>
        </section>
"""


# Fotos del pase de la portada (fotosdefinitivas/web/portada/portada-N-1920.jpg y -1280.jpg).
# Cada una se descarga justo antes de mostrarse; la primera, enseguida.
HERO_SLIDES = [
    "Eucaristía dominical",
    "Nuestro campanario",
    "Domingo de Ramos",
    "La comunidad en la plaza",
    "Bendición de los ramos",
    "Una parroquia viva",
]

INDEX_HEAD = """    <link rel="preload" as="image" href="fotosdefinitivas/web/portada/portada-1-1920.jpg" media="(min-width: 1281px)" fetchpriority="high">
    <link rel="preload" as="image" href="fotosdefinitivas/web/portada/portada-1-1280.jpg" media="(max-width: 1280px)" fetchpriority="high">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Church",
      "@id": "https://parroquiasantateresabcn.netlify.app/#parroquia",
      "name": "Parroquia Santa Teresa de Jesús",
      "alternateName": ["Parròquia de Santa Teresa de Jesús", "Parroquia de Santa Teresa de Jesús de Barcelona", "Santa Teresa de Jesús (El Carmel)"],
      "description": "Parroquia católica del barrio del Carmel, en Barcelona, perteneciente al Arzobispado de Barcelona.",
      "url": "https://parroquiasantateresabcn.netlify.app/",
      "logo": "https://parroquiasantateresabcn.netlify.app/favicon-512.png",
      "hasMap": "https://goo.gl/maps/Y4SiUkiMGwp",
      "parentOrganization": { "@type": "Organization", "name": "Arzobispado de Barcelona", "url": "https://esglesia.barcelona/" },
      "image": "https://parroquiasantateresabcn.netlify.app/fotosdefinitivas/web/portada3.jpg",
      "email": "albertsols@gmail.com",
      "telephone": "+34 619 040 913",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Carrer del Llobregós, 132",
        "postalCode": "08032",
        "addressLocality": "Barcelona",
        "addressCountry": "ES"
      },
      "geo": { "@type": "GeoCoordinates", "latitude": 41.4242, "longitude": 2.1558 },
      "isAccessibleForFree": true,
      "publicAccess": true,
      "sameAs": ["https://www.instagram.com/p.santateresadejesusbcn/"]
    }
    </script>
"""

def _first_quote(text):
    m = re.search(r"(?m)^>\s*(.+)$", text or "")
    return m.group(1).strip() if m else ""


def _portrait(h, depth, cls="priest-photo"):
    p = "../" * depth
    if h["autor_foto"]:
        return f'<div class="{cls}"><img src="{p}{h["autor_foto"]}" alt="{esc(h["autor_nombre"])}" loading="lazy"></div>'
    return f'<div class="{cls} no-photo">{LOGO_MARK}</div>'


MES_CORTO = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def date_long(h, cls=""):
    """Fecha larga; el JavaScript la escribe en el idioma de la página (no la toca el traductor)."""
    if not h.get("fecha"):
        return ""
    c = f' class="{cls}"' if cls else ""
    return f'<time{c} datetime="{h["fecha"]}" data-fmt="long">{HOM.fecha_larga(h["fecha"])}</time>'


def date_badge(h):
    """Calendario pequeño con día, mes y año."""
    try:
        y, m, d = h["fecha"].split("-")
        m = int(m)
    except (ValueError, KeyError):
        return ""
    return (f'<time class="date-badge" datetime="{h["fecha"]}" data-fmt="badge">'
            f'<span class="db-d">{int(d)}</span><span class="db-m">{MES_CORTO[m - 1]}</span><span class="db-y">{y}</span></time>')


def new_badge(h):
    """Etiqueta «Nueva»: el JavaScript la muestra solo durante los 30 días siguientes a la fecha."""
    return f'<span class="new-badge" data-new="{h["fecha"]}" hidden>Nueva</span>' if h.get("fecha") else ""


def notice_text(h):
    txt = _first_quote(h.get("texto")) or h["extracto"]
    return txt[:150].rsplit(" ", 1)[0] + "…" if len(txt) > 150 else txt


def ultima_template(depth):
    """Aviso automático de la última reflexión: cada página lo lleva en un <template> (así se
    traduce y enlaza igual que el resto) y site.js lo muestra una vez a cada visitante."""
    if not HOMILIAS:
        return ""
    h = HOMILIAS[0]
    p = "../" * depth
    txt = notice_text(h)
    foto = (f'<div class="notice-photo"><img src="{p}{h["autor_foto"]}" alt=""></div>' if h["autor_foto"]
            else f'<div class="notice-photo no-photo">{LOGO_MARK}</div>')
    return f"""
    <template id="pst-ultima" data-id="reflexion-{h["slug"]}" data-fecha="{h["fecha"]}" data-slug="{h["slug"]}">
        {foto}
        <div class="notice-body">
            <span class="notice-tag"><span class="notice-dot" aria-hidden="true"></span><span data-when="new">Nueva reflexión</span><span data-when="old">Última reflexión</span></span>
            <h3>{esc(h["titulo"])}</h3>
            <p class="notice-meta"><span>{esc(h["autor_nombre"])}</span> · {date_long(h)}</p>
            <p class="notice-quote">{esc(txt)}</p>
            <a class="btn btn-solid notice-go" href="{p}{h["url"]}">Leer la reflexión <span aria-hidden="true">&rarr;</span></a>
        </div>
    </template>"""


def home_homily():
    if not HOMILIAS:
        return ""
    h = HOMILIAS[0]
    body_md, truncated = HOM.home_text(h.get("texto", ""))
    quote = _first_quote(h.get("texto"))
    quote_html = (f'<blockquote class="book-quote"><span aria-hidden="true">&ldquo;</span>{esc(quote)}</blockquote>' if quote else "")
    others = "".join(
        f"""
                <a class="homily-chip" href="{o["url"]}" style="--author:{o["autor_color"]}">
                    {_portrait(o, 0, "chip-photo")}
                    <span><strong>{esc(o["titulo"])}</strong><em><span>{esc(o["autor_nombre"])}</span> · {date_long(o)}</em></span>
                </a>""" for o in HOMILIAS[1:3])
    return f"""        <section id="reflexion" class="homily">
            <div class="section-head">
                <span class="subtitulo">De nuestra parroquia</span>
                <h2>Reflexión dominical</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="open-book" style="--author:{h["autor_color"]}">
                <span class="book-ribbon" aria-hidden="true"></span>
                <div class="book-leaf book-left">
                    {_portrait(h, 0)}
                    <strong class="book-author">{esc(h["autor_nombre"])}</strong>
                    <span class="book-role">{esc(h["autor_cargo"])}</span>
                    <span class="book-date">{date_long(h)}</span>
                    {ORNAMENT}
                    {quote_html}
                    <a href="{h["url"]}" class="btn btn-solid">Leer la reflexión completa</a>
                </div>
                <div class="book-leaf book-right">
                    <article class="homily-text">
                        {new_badge(h)}<span class="book-kicker">{esc(h["kicker"]) or date_long(h)}</span>
                        <h3>{esc(h["titulo"])}</h3>
                        <div class="homily-body">
{HOM.markdown(body_md, indent="                            ")}
                        </div>
                    </article>
                    <a href="{h["url"]}" class="link-arrow book-more">Seguir leyendo <span>&rarr;</span></a>
                    <span class="book-ornament" aria-hidden="true">{LOGO_MARK}</span>
                </div>
            </div>
            <div class="homily-more">
                <span class="subtitulo">Otras reflexiones</span>
                <div class="homily-chips">{others}
                </div>
                <a href="html/humiliasmenu.html" class="link-arrow">Ver todas las reflexiones <span>&rarr;</span></a>
            </div>
        </section>
"""


HOME_HOMILY = home_homily()

# ---------------------------------------------------------------- INDEX
ICON_SUN = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ICON_MOON = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
ICON_CROSS = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><path d="M12 2v20M6 8h12"/><circle cx="12" cy="8" r="2.4"/></svg>'
ICON_HEART = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>'


def feature(photo, eyebrow, title, text, link):
    return f"""                <a class="feature" href="{link}">
                    <img src="{img(photo, 0)}" alt="{title}" loading="lazy">
                    <div class="feature-body">
                        <span class="subtitulo">{eyebrow}</span>
                        <h3>{title}</h3>
                        <p>{text}</p>
                    </div>
                </a>"""


PAGES["index.html"] = page(0, "", "Parroquia Santa Teresa de Jesús, en el barrio del Carmel (Barcelona). Horarios de eucaristías, actividades pastorales y contacto.",
full_title="Parroquia Santa Teresa de Jesús | Barcelona", active="portada", extra_head=INDEX_HEAD, body="""        <section class="hero hero-slider">
            <div class="hero-bg hero-slides" aria-hidden="true">""" + "".join(
    f'\n                <span class="hero-slide{" is-on ready" if i == 1 else ""}"><em>{cap}</em></span>'
    for i, cap in enumerate(HERO_SLIDES, 1)) + """
            </div>
            <span class="eyebrow">Parroquia · El Carmel · Barcelona</span>
            <h1>Santa Teresa<br>de Jesús</h1>
            <div class="hero-divider"></div>
            <p>C/ Llobregós, 132 · 08032 Barcelona</p>
            <div class="next-mass" data-next-mass hidden></div>
            <div class="hero-actions">
                <a href="#horarios" class="btn btn-solid">Horarios de misa</a>
                <a href="#bienvenida" class="btn btn-light">Conócenos</a>
            </div>
            <a href="#horarios" class="scroll-cue" aria-label="Bajar a los horarios"></a>
            <div class="hero-slider-ui" aria-hidden="true">
                <span class="hero-caption" data-hero-caption></span>
                <span class="hero-dots">""" + "".join('<i></i>' for _ in HERO_SLIDES) + """</span>
            </div>
        </section>

        <section id="horarios" class="schedule-section">
            <div class="schedule-card">
                <div class="schedule-item" data-days="1,2,3,4,5">
                    """ + ICON_SUN + """
                    <h3>Laborables</h3>
                    <div class="time">19:00 <small>h</small></div>
                    <p>Eucaristía</p>
                </div>
                <div class="schedule-item" data-days="6">
                    """ + ICON_MOON + """
                    <h3>Sábados</h3>
                    <div class="time">19:00 <small>h</small></div>
                    <p>Eucaristía</p>
                </div>
                <div class="schedule-item" data-days="0">
                    """ + ICON_CROSS + """
                    <h3>Domingos</h3>
                    <div class="time">11:00 <small>·</small> 13:15</div>
                    <p>Eucaristía · 11:00 h con coro góspel</p>
                </div>
                <div class="schedule-item" data-days="6">
                    """ + ICON_HEART + """
                    <h3>Confesiones</h3>
                    <div class="time">18:30 <small>h</small></div>
                    <p>Sábados, y antes de cada misa</p>
                </div>
            </div>
            <div class="schedule-foot">
                <a href="html/misas.html" class="link-arrow">Calendario de eucaristías y actividades <span>&rarr;</span></a>
            </div>
        </section>

        <section id="bienvenida">
            <div class="two-col center">
                <div class="framed-img">
                    <img src=\"""" + img("nuevalife.jpeg", 0) + """\" alt="Campanario y fachada de la Parroquia Santa Teresa de Jesús" loading="lazy">
                    <div class="badge"><span>Desde</span><strong data-count="1924" data-from="1850">1924</strong></div>
                </div>
                <div>
                    <span class="subtitulo text-left">Bienvenidos</span>
                    <h2 class="text-left">Una parroquia en el corazón del Carmel</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <p>La iglesia se construyó en 1924 en terrenos de la antigua finca de Can Grau, y desde un primer momento estuvo muy integrada en el barrio: fue sede de una de las primeras cooperativas obreras y de una escuela para niños y adultos.</p>
                    <div class="stats">
                        <div><strong data-count="1928" data-from="1850">1928</strong><span>Bendición del templo</span></div>
                        <div><strong data-count="100" data-prefix="+">+100</strong><span>Años en el barrio</span></div>
                        <div><strong data-count="14">14</strong><span>Grupos y servicios</span></div>
                    </div>
                    <div class="btn-group">
                        <a href="html/historia.html" class="btn">Nuestra historia</a>
                        <a href="html/organigramaparroquial.html" class="link-arrow" style="align-self:center;">Organigrama <span>&rarr;</span></a>
                    </div>
                </div>
            </div>
        </section>

        <section class="image-band" data-bg="fotosdefinitivas/web/portada2.jpg">
            <div class="quote">
                <span class="quote-mark" aria-hidden="true">&ldquo;</span>
                <blockquote>Nada te turbe, nada te espante, todo se pasa, Dios no se muda; la paciencia todo lo alcanza; quien a Dios tiene nada le falta. Sólo Dios basta.</blockquote>
                <cite>Santa Teresa de Jesús</cite>
            </div>
        </section>

""" + HOME_HOMILY + """
        <section id="vida" class="section-warm">
            <div class="section-head">
                <span class="subtitulo">Dinámica pastoral</span>
                <h2>Vida parroquial</h2>
                <hr class="section-divider" style="margin-bottom:1.25rem;">
                <p>Grupos, celebraciones y servicios que dan vida a nuestra comunidad durante todo el año.</p>
            </div>
            <div class="feature-grid">
""" + "\n".join([
    feature("DSC_0448.JPG", "Domingos 11:00 h", "Misa con coro góspel", "Todos los domingos (salvo en agosto) canta un amplio grupo de góspel en la misa de las 11:00.", "html/misas.html"),
    feature("DSC_0586.JPG", "Niños y adolescentes", "Catequesis", "Preparación para la primera comunión y la confirmación. Inscripciones abiertas.", "html/catequesis.html"),
    feature("caritas.jpg", "Solidaridad", "Cáritas parroquial", "Un día al mes repartimos alimentos a varias docenas de familias del barrio.", "html/dinamicapastoral.html"),
    feature("IMG_5495.jpg", "Grupo de jóvenes", "Jóvenes", "Cada 8 sábados aproximadamente comentamos con el rector el evangelio del domingo.", "html/jovenes2alternativa.html"),
]) + """
            </div>
            <div class="btn-group center" style="margin-top:3rem;">
                <a href="html/dinamicapastoral.html" class="btn">Ver toda la dinámica pastoral</a>
            </div>
        </section>

        <section id="sacramentos">
            <div class="section-head">
                """ + ORNAMENT + """
                <span class="subtitulo">Celebrar la fe</span>
                <h2>Sacramentos</h2>
                <p>Te acompañamos en los momentos más importantes de la vida cristiana.</p>
            </div>
            <div class="icon-grid five">
""" + "\n".join([
    icon_card("agua", "Bautismo", "Ceremonias bautismales al mediodía en cualquier domingo del año que se pida.", "html/bautismo.html"),
    icon_card("paloma", "Confirmación", "Se celebra cada tres años, con catequesis a partir de los 14 años.", "html/confirmacion.html"),
    icon_card("anillos", "Matrimonio", "Bodas, preparación y aniversarios de plata, oro o diamante: consulta en el despacho los viernes por la tarde.", "html/matrimonio.html"),
    icon_card("manos", "Perdón", "Los sábados de 18:30 a 19:00 h y siempre un rato antes de cada misa.", "html/perdon.html"),
    icon_card("oleo", "Unción de los enfermos", UNCION_TXT, "html/uncion.html"),
]) + """
            </div>
        </section>

        <section id="galeria" class="section-warm">
            <div class="section-head">
                <span class="subtitulo">Galería</span>
                <h2>La parroquia en imágenes</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
""" + mosaic(GALLERY, 0) + """
            <div class="btn-group center" style="margin-top:3rem;">
                <a href="html/imagenes.html" class="btn">Más fotos y vídeos</a>
            </div>
        </section>

        <section id="actualidad" class="section-alt">
            <div class="section-head" style="margin-bottom:0;">
                <span class="subtitulo">Vida Parroquial</span>
                <h2>Actualidad y Evangelio</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <a class="family-entry family-entry-top" href="html/evangelio-familia.html">
                <span class="family-entry-img" style="background-image:url('fotosdefinitivas/web/familia-pixelada.jpg')" aria-hidden="true"></span>
                <span class="family-entry-body">
                    <span class="subtitulo">Para leer en casa</span>
                    <strong>El Evangelio para la familia</strong>
                    <span class="family-entry-text">Cada día, el Evangelio explicado para los niños: texto, comentario, ilustración y juegos para leerlo juntos.</span>
                    <span class="btn btn-solid">Leer en familia</span>
                </span>
            </a>
            <div class="act-actions">
                <a href="https://evangeli.net/evangelio" class="btn btn-solid" target="_blank" rel="noopener">Leer el Evangelio de hoy completo &rarr;</a>
                <a href="html/noticias.html" class="btn">Noticias del Vaticano y del Arzobispado &rarr;</a>
            </div>

            <div class="grid-container">
                <div class="widget-container">
                    <h3>Evangelio de Hoy</h3>
                    <div class="gospel-day">
                        <span class="gospel-date" data-hoy>Hoy</span>
                        <strong class="gospel-liturgia" data-liturgia>Evangelio del día</strong>
                        <p class="gospel-sign">Una invitación diaria de la Parroquia Santa Teresa de Jesús a leer y orar con la Palabra de Dios.</p>
                    </div>
                    <script src="js/liturgia.js?v=""" + V["js/liturgia.js"] + """" defer></script>
                    <div class="gospel-frame">
                        <iframe title="Evangelio de hoy" width="100%" height="680" frameborder="0" loading="lazy" src="https://evangeli.net/evangelio/widget/web"></iframe>
                    </div>
                </div>

                <div class="widget-container">
                    <h3>@p.santateresadejesusbcn</h3>
                    <div class="ig-card">
                    """ + ig_profile(0, "flat") + """
                    """ + ig_grid(0) + """
                    <a class="btn btn-solid ig-more" href="""" + IG_URL + """" target="_blank" rel="noopener">Ver las últimas publicaciones en Instagram &rarr;</a>
                    </div>
                </div>
            </div>

        </section>
""" + revista_module(0) + """

        <section class="visit">
            <div class="two-col center">
                <figure class="visit-img">
                    <img src="fotosdefinitivas/web/vidriera.jpg" alt="Vidriera de Santa Teresa de Jesús con el Niño" loading="lazy">
                    <figcaption>Vidriera de Santa Teresa con el Niño Jesús</figcaption>
                </figure>
                <div>
                    <span class="subtitulo text-left">Te esperamos</span>
                    <h2 class="text-left">Visítanos</h2>
                    <hr class="section-divider" style="margin-left:0; margin-bottom:2rem;">
                    <p>Las puertas de la parroquia están abiertas para todos. Ven a celebrar la eucaristía con nosotros o a hablar con el párroco: bautizos, bodas, visitas a enfermos o cualquier consulta.</p>
                    <ul class="info-list" style="margin:1.5rem 0 2rem;">
                        <li><strong>Dirección</strong>Carrer del Llobregós, 132 — 08032 Barcelona</li>
                        <li><strong>Despacho parroquial</strong>Viernes por la tarde, y antes o después de cada misa</li>
                    </ul>
                    <div class="btn-group">
                        <a href="html/contacto.html#escribenos" class="btn btn-solid">Escríbenos</a>
                        <a href=\"tel:""" + TEL + """\" class="btn btn-light btn-call">""" + ICON_PHONE + """<span>Llamar a la parroquia</span></a>
                    </div>
                </div>
            </div>
        </section>

""" + location_block() + """""")

# ---------------------------------------------------------------- DINÁMICA PASTORAL
FLIP = [
    ("DSC_0448.JPG", "Misa dominical de las 11:00h y actos eucarísticos",
     "De las misas que se celebran durante el fin de semana, desde el punto de vista de animación, destaca la de las 11:00h.",
     "Misa dominical de las 11:00h y actos eucarísticos",
     "De las misas que se celebran durante el fin de semana, desde el punto de vista de animación, destaca la de las 11:00h. Todos los domingos (salvo en agosto) canta un amplio grupo de Góspel en dicha misa.",
     ("misas.html", "Ver horarios", False)),
    ("IMG_5471.jpg", "Administración de otros Sacramentos",
     "Mn. Sols administra el sacramento del Perdón de manera fija los sábados.",
     "Administración de otros Sacramentos",
     "Mn. Sols administra el sacramento del Perdón de manera fija los sábados de 18:30-19:00 horas y siempre un rato antes de cada misa. Hay ceremonias bautismales al mediodía en cualquier domingo del año que se le pida. Cada tres años se celebra la Confirmación.",
     ("adminsacra.html", "Sacramentos", False)),
    ("caritas.jpg", "Cáritas parroquial y equipo arciprestal de Cáritas",
     "La labor que realiza Cáritas parroquial consiste en repartir alimentos, un día al mes, a varias docenas de familias.",
     "Cáritas parroquial y equipo arciprestal de Cáritas",
     "La labor que realiza Cáritas parroquial consiste en repartir alimentos, un día al mes, a varias docenas de familias. Se ha creado un consejo de Cáritas, de ámbito Arciprestal, para unificar criterios.",
     None),
    ("catequesis.png", "Catequesis",
     "Niños y adolescentes reciben, de forma periódica, una formación cristiana.",
     "Catequesis primera comunión y confirmación",
     "Niños y adolescentes reciben, de forma periódica, una formación cristiana que les prepara para recibir el sacramento de la eucaristía y el de la confirmación (este último a partir de los 14 años).",
     ("catequesis.html", "Inscripciones", False)),
    ("familia.jpg", "Equipo de matrimonios y parejas",
     "Cada 8 sábados, por la noche, un grupo de 6 o 7 matrimonios trabaja, con ayuda del rector, algún documento del papa.",
     "Equipo de matrimonios y parejas",
     "Cada 8 sábados, por la noche, un grupo de 6 o 7 matrimonios trabaja, con ayuda del rector, algún documento del papa. La reunión dura 1h y se realiza un pequeño pica pica.",
     None),
    ("rezando.jpg", "Atención pastoral a enfermos",
     "Mn. Sols atiende a gente mayor en sus casas el domingo último de cada mes, ayudado por un grupo de voluntarios.",
     "Atención pastoral a enfermos",
     "Mn. Sols atiende a gente mayor en sus casas el domingo último de cada mes si estos así lo solicitan mediante las vías de contacto de la web y es ayudado por un grupo de voluntarios que van a residencias de la tercera edad.",
     ("contacto.html?motivo=Visita%20a%20enfermos#escribenos", "Solicitar visita", False)),
    ("IMG_5495.jpg", "Equipo de jóvenes",
     "Cada 8 sábados aproximadamente un pequeño grupo de jóvenes comentan con el rector el evangelio del domingo.",
     "Equipo de jóvenes",
     "Por otro lado, cada 8 sábados aproximadamente, un pequeño grupo de jóvenes, acompañados de algún matrimonio, comentan con el rector el evangelio del domingo.",
     ("jovenes2alternativa.html", "Jóvenes", False)),
    ("equipoespiritualidad.jpeg", "Equipo de espiritualidad eucarística",
     "Grupo de señoras que se reúne cada mes con una religiosa quien las enriquece en el fervor a la Eucaristía.",
     "Equipo de espiritualidad eucarística",
     "Grupo de señoras que se reúne cada mes con una religiosa quien las enriquece en el fervor a la Eucaristía y cada miércoles, a las 19:30 horas, hay una media hora de bendición con adoración al Santísimo.",
     None),
    ("limpieza.jpg", "Voluntariado de limpieza",
     "Desde hace muchos años, un equipo de personas voluntarias limpia la iglesia una vez al mes.",
     "Voluntariado de limpieza",
     "Una peculiaridad de nuestra parroquia es que un equipo de personas limpian la iglesia un día al mes; lo hacen de manera voluntaria desde hace ya muchos años.",
     None),
    ("salidas.png", "Salidas parroquiales",
     "Cada año cuando es factible, hay una salida por Pascua: una jornada con Mn. Sols para consolidar la comunidad.",
     "Salidas parroquiales",
     "Cada año cuando es factible, hay una salida por Pascua: una jornada con Mn. Sols donde la convivencia y el descanso ayudan a consolidar la comunidad parroquial.",
     None),
    ("DSC_0568.JPG", "Despacho parroquial, bautizos y bodas",
     "Hay un despacho parroquial de 6 a 7 de la tarde donde toda persona se encuentra con Mn. Sols para consultarle cosas diversas.",
     "Despacho parroquial",
     "Los viernes por la tarde y de hecho un rato antes o después de todas las misas de la semana, el cura párroco atiende a gente para cualquier tipo de asuntos.",
     ("contacto.html", "Contacto", False)),
    ("santateresa.jpg", "Charlas semanales de formación",
     "Los viernes, al acabar la misa vespertina, se imparten charlas de formación sobre espiritualidad litúrgica, bíblica y moral católica.",
     "Charlas semanales de formación",
     "Los viernes, al acabar la misa vespertina, se imparten charlas de formación sobre espiritualidad litúrgica, bíblica y moral católica.",
     None),
    ("colegio.jpeg", "Colegio Santa Teresa",
     "No es propiamente un centro educativo parroquial pero se respeta el humanismo cristiano en su didáctica escolar.",
     "Colegio Santa Teresa",
     "No es propiamente un centro educativo parroquial pero se respeta el humanismo cristiano en su didáctica escolar. Son arrendatarios del patrimonio parroquial. Entre el director-propietario del Colegio y el rector hay muy buena relación.",
     ("https://agora.xtec.cat/colegiosantateresa", "Web del Colegio", True)),
    ("vidacreixent.jpg", "«Vida Creixent»",
     "El movimiento Vida Creixent es un grupo de personas mayores que se reúnen dos veces al mes.",
     "«Vida Creixent»",
     "El movimiento Vida Creixent es un grupo de personas mayores que se reúnen dos veces al mes. Está dirigido por una religiosa que guía su formación y convivencia.",
     None),
]


def flip_card(photo, t1, p1, t2, p2, link):
    a = ""
    if link:
        url, label, external = link
        extra = ' target="_blank" rel="noopener"' if external else ""
        a = f'\n                        <a href="{url}"{extra}>{label}</a>'
    return f"""                <article class="flip-card" tabindex="0">
                    <div class="flip-inner">
                        <div class="flip-front">
                            <img src="{img(photo)}" alt="{t1}" loading="lazy">
                            <div class="flip-body">
                                <h3>{t1}</h3>
                                <p>{p1}</p>
                                <span class="flip-hint">Saber más &rarr;</span>
                            </div>
                        </div>
                        <div class="flip-back">
                            <h3>{t2}</h3>
                            <p>{p2}</p>{a}
                        </div>
                    </div>
                </article>"""


PAGES["html/dinamicapastoral.html"] = page(1, "Dinámica Pastoral", "Grupos, servicios y actividades pastorales de la Parroquia Santa Teresa de Jesús de Barcelona.", active="dinamica", body=page_hero("Vida de la comunidad", "Dinámica Pastoral", "web/portada2.jpg") + """
        <section>
            <span class="subtitulo">Grupos y servicios</span>
            <h2>Lo que hacemos</h2>
            <hr class="section-divider">
            <div class="flip-grid">
""" + "\n".join(flip_card(*f) for f in FLIP) + """
            </div>
        </section>

        <section class="section-warm" id="momentos">
            <div class="section-head">
                <span class="subtitulo">Salidas, celebraciones y vida parroquial</span>
                <h2>Momentos de la comunidad</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
""" + mosaic(MOMENTOS, 1) + """
            <div class="btn-group center" style="margin-top:2.5rem;">
                <a href="imagenes.html" class="btn">Más fotos y vídeos</a>
            </div>
        </section>
""")

# ---------------------------------------------------------------- ORGANIGRAMA
PAGES["html/organigramaparroquial.html"] = page(1, "Organigrama Parroquial", "Estructura, consejo parroquial y consejo económico de la Parroquia Santa Teresa de Jesús.", active="organigrama", body=page_hero("Cómo nos organizamos", "Organigrama Parroquial") + """
        <section id="estructura">
            <div class="section-head">
                <span class="subtitulo">Nuestra estructura</span>
                <h2>Organigrama</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="org-chart">
                <div class="org-node org-top">
                    <div class="icon-circle">""" + SAC_ICONS["persona"] + """</div>
                    <span class="subtitulo">Rector parroquial</span>
                    <h3>Mn. Albert Sols</h3>
                </div>
                <div class="org-branches">
                    <div class="org-node">
                        <div class="icon-circle">""" + SAC_ICONS["grupo"] + """</div>
                        <h3>Consejo parroquial</h3>
                        <p>Una docena de miembros de la comunidad, uno por cada ámbito pastoral. Se convoca cada trimestre.</p>
                    </div>
                    <div class="org-node">
                        <div class="icon-circle">""" + SAC_ICONS["cuentas"] + """</div>
                        <h3>Consejo económico</h3>
                        <p>Tres feligreses con cultura de contabilidad. Se convoca al final de cada trimestre.</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="section-warm" id="consejos">
            <div class="two-col">
                <div class="prose">
                    <h3>Consejo parroquial</h3>
                    <p>Lo integran una docena de miembros de la comunidad bajo la presidencia del rector, quien es asesorado en la marcha conjunta de la parroquia. Cada consejero representa un ámbito pastoral.</p>
                    <p>Las decisiones no son vinculantes y este consejo facilita que la parroquia camine de forma armonizada sin marginar ninguna actividad pastoral. Se convoca cada trimestre.</p>
                </div>
                <div class="prose">
                    <h3>Consejo económico</h3>
                    <p>Se convoca al final de cada trimestre y lo forman tres feligreses con cierta cultura de contabilidad. Ayudan al rector a elaborar las engorrosas cuentas anuales que deben ser presentadas a la curia. Dan su opinión a obras de conservación y mejora aportando criterio al rector para una prudente realización.</p>
                </div>
            </div>
        </section>
""")

# ---------------------------------------------------------------- HISTORIA
PAGES["html/historia.html"] = page(1, "Historia", "Historia y archivo fotográfico de la Parroquia Santa Teresa de Jesús, en el Carmel (Barcelona), desde 1924.", active="historia", body=page_hero("Desde 1924", "Nuestra Historia", "web/nuevalife.jpg", "Historia", "center 15%") + """
        <section id="parroquia">
            <div class="two-col center">
                <div class="prose">
                    <span class="subtitulo text-left">El Carmel, Barcelona</span>
                    <p class="lead">La parroquia de Santa Teresa de Jesús está situada en el corazón del Carmel, Barcelona.</p>
                    <p>Desde un primer momento la parroquia estuvo muy integrada en el barrio, pues fue la sede de una de las primeras cooperativas obreras del barrio y una escuela para niños y adultos.</p>
                </div>
                <div class="framed-img">
                    <img src=\"""" + img("nuevalife.jpeg") + """\" alt="Campanario y fachada de la parroquia" loading="lazy">
                </div>
            </div>
        </section>

        <section class="section-warm" id="linea-del-tiempo">
            <div class="section-head">
                <span class="subtitulo">Un siglo de historia</span>
                <h2>Línea del tiempo</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="year" data-count="1923" data-from="1900">1923</div>
                    <h3>La primera piedra</h3>
                    <p>Hemos localizado unas fotografías pertenecientes a la colocación de la 1ª piedra de nuestra querida parroquia, fechadas en 1923 (posiblemente en el mes de mayo).</p>
                </div>
                <div class="timeline-item">
                    <div class="year" data-count="1924" data-from="1900">1924</div>
                    <h3>Construcción de la iglesia</h3>
                    <p>La iglesia se construyó en terrenos de la antigua finca de Can Grau (actual cruce entre Llobregós y Conca de Tremp) y era tenencia parroquial de Sant Joan d'Horta.</p>
                </div>
                <div class="timeline-item">
                    <div class="year" data-count="1927" data-from="1900">1927</div>
                    <h3>Un templo sencillo y su campanario</h3>
                    <p>Terminan las obras levantadas desde 1923: una iglesia de una sola nave y, a su lado, el campanario de 17,82 metros que todavía hoy marca la silueta del barrio.</p>
                    <details class="tl-more">
                        <summary>Seguir leyendo</summary>
                        <p>La nave se cubre con un techo de vigas que descansa sobre dos arcos de medio punto, y termina en un ábside semicircular. Los muros, encalados, dan al interior esa luz blanca tan característica. A la entrada se encuentran el cancel y el coro.</p>
                        <p>Delante de la iglesia se abre un atrio porticado de tres arcos de medio punto —el central, más alto— apoyados en columnas sobre un muro bajo y cerrado con rejas.</p>
                        <p>El campanario, de la misma época que el templo, es sencillo y funcional: planta casi cuadrada, cornisa moldurada, tejado a cuatro aguas y una ventana de arco en cada cara. Sus muros, revocados y pintados en tono crema, se adosan al muro sur, junto al porche.</p>
                        <p class="tl-source">Según la ficha de la parroquia en el inventario de campanarios de Cataluña (campaners.com).</p>
                    </details>
                </div>
                <div class="timeline-item">
                    <div class="year" data-count="1928" data-from="1900">1928</div>
                    <h3>Bendición del templo</h3>
                    <p>Su bendición se produjo en octubre de 1928, tal como recoge la reseña de La Vanguardia del día 20.</p>
                </div>
                <div class="timeline-item">
                    <div class="year" data-count="2005" data-from="1900">2005</div>
                    <h3>El hundimiento del túnel</h3>
                    <p>En febrero de 2005 la parroquia se situó en el centro de las miradas, al estar afectada por el desgraciado hundimiento del túnel de maniobra durante las obras del metro. El patio de la iglesia está situado justo enfrente, al otro lado de la calle, de donde se formó el agujero.</p>
                </div>
                <div class="timeline-item timeline-now">
                    <div class="year">Hoy</div>
                    <h3>Un siglo de vida en el Carmel</h3>
                    <p>Cien años después de su construcción, la parroquia sigue siendo un punto de encuentro del barrio: la misa dominical con coro góspel, la catequesis de niños y adolescentes, Cáritas, los grupos de jóvenes y de matrimonios, y una comunidad que continúa abierta a todos.</p>
                    <a href="dinamicapastoral.html" class="link-arrow">Conoce la vida parroquial <span>&rarr;</span></a>
                </div>
            </div>
        </section>

        <section id="archivo" class="archive-section">
            <div class="section-head">
                <span class="subtitulo">Álbum de la parroquia</span>
                <h2>Nuestra iglesia en imágenes</h2>
                <hr class="section-divider" style="margin-bottom:1.25rem;">
                <p>Rincones, celebraciones y detalles de un templo que acompaña al barrio desde hace un siglo. Pulsa una foto para verla en grande.</p>
            </div>
            <div class="mosaic archive-album">
                <a href="../fotosdefinitivas/web/nuevalife.jpg" class="print tall"><img src="../fotosdefinitivas/web/nuevalife.jpg" alt="El campanario y la fachada de la iglesia" loading="lazy"><span class="print-caption">El campanario</span></a>
                <a href="../fotosdefinitivas/web/dsc_0541.jpg" class="print wide"><img src="../fotosdefinitivas/web/dsc_0541.jpg" alt="Interior de la iglesia durante la eucaristía" loading="lazy"><span class="print-caption">La nave durante la eucaristía</span></a>
                <a href="../fotosdefinitivas/web/vidriera.jpg" class="print tall"><img src="../fotosdefinitivas/web/vidriera.jpg" alt="Vidriera de Santa Teresa con el Niño Jesús" loading="lazy"><span class="print-caption">La vidriera de Santa Teresa</span></a>
                <a href="../fotosdefinitivas/web/dsc_0574.jpg" class="print"><img src="../fotosdefinitivas/web/dsc_0574.jpg" alt="Imágenes del presbiterio" loading="lazy"><span class="print-caption">El presbiterio</span></a>
                <a href="../fotosdefinitivas/web/img_5493.jpg" class="print"><img src="../fotosdefinitivas/web/img_5493.jpg" alt="Capilla del Santísimo" loading="lazy"><span class="print-caption">La capilla del Santísimo</span></a>
                <a href="../fotosdefinitivas/web/dsc_0599webog.jpg" class="print"><img src="../fotosdefinitivas/web/dsc_0599webog.jpg" alt="El campanario durante el Domingo de Ramos" loading="lazy"><span class="print-caption">Domingo de Ramos</span></a>
                <a href="../fotosdefinitivas/web/dsc_0546.jpg" class="print wide"><img src="../fotosdefinitivas/web/dsc_0546.jpg" alt="La iglesia llena durante una celebración" loading="lazy"><span class="print-caption">La comunidad reunida</span></a>
                <a href="../fotosdefinitivas/web/dsc_0589.jpg" class="print"><img src="../fotosdefinitivas/web/dsc_0589.jpg" alt="Bendición de ramos en el Domingo de Ramos" loading="lazy"><span class="print-caption">La bendición de los ramos</span></a>
            </div>
            <div class="archive-invite">
                <span class="archive-invite-icon" aria-hidden="true">""" + LOGO_MARK + """</span>
                <div>
                    <strong>¿Guardas fotos antiguas de la parroquia?</strong>
                    <p>Estamos recuperando el archivo histórico: la colocación de la primera piedra en 1923, la bendición de 1928 y la vida del barrio. Si tienes fotografías, escríbenos y las incorporaremos.</p>
                </div>
                <a href="contacto.html?motivo=Archivo%20histórico#escribenos" class="btn">Compartir fotos</a>
            </div>
        </section>
""")

# ---------------------------------------------------------------- CONTACTO
# Motivos del formulario: (valor que llega en el correo, texto del botón, ayuda para el mensaje).
# Otras páginas enlazan a contacto.html?motivo=<valor>#escribenos y el motivo llega ya marcado.
MOTIVOS = [
    ("Consulta general", "Consulta general", "Cuéntanos en qué podemos ayudarte"),
    ("Bautizo", "Bautizo", "Nombre del bebé, su fecha de nacimiento y el domingo que os gustaría"),
    ("Boda", "Boda", "Vuestros nombres y la fecha aproximada que tenéis pensada"),
    ("Aniversario de boda", "Aniversario de boda", "Qué aniversario celebráis (plata, oro, diamante…) y la fecha que os gustaría"),
    ("Primera Comunión", "Primera Comunión", "Nombre del niño o la niña, edad y curso escolar"),
    ("Confirmación", "Confirmación", "Nombre y edad de quien quiere confirmarse"),
    ("Sacramento del Perdón", "Perdón (confesión)", "Si necesitas otro horario distinto al de los sábados, dinos cuándo te va bien"),
    ("Visita a enfermos", "Visita a enfermos", "Nombre de la persona, dirección y qué días va mejor"),
    ("Unción de los enfermos", "Unción de los enfermos", "Nombre de la persona, dónde está (casa, hospital o residencia) y un teléfono. Si es urgente, mejor llama"),
    ("Funeral", "Funeral", "Nombre del difunto y fecha prevista. Te llamaremos cuanto antes"),
    ("Cáritas", "Cáritas", "Cuéntanos qué necesitas o cómo te gustaría colaborar"),
    ("Grupo de jóvenes", "Grupo de jóvenes", "Tu edad y cómo te has enterado del grupo"),
    ("Archivo histórico", "Fotos antiguas", "Qué fotos tienes, de qué año aproximado y de qué celebración"),
    ("Otro", "Otro", "Cuéntanos en qué podemos ayudarte"),
]
PAGES["html/contacto.html"] = page(1, "Contacto", "Contacta con la Parroquia Santa Teresa de Jesús: Carrer del Llobregós, 132, 08032 Barcelona.", active="contacto", body=page_hero("Estamos para ayudarte", "Contacto", "web/portada1.jpg") + """
        <section class="contact-main" id="escribenos">
            <span id="datos" class="anchor-alias"></span>
            <div class="two-col">
                <div>
                    <span class="subtitulo text-left">Escríbenos</span>
                    <h2 class="text-left">Contacta con nosotros</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <form class="mail-form form-contact" action=\"""" + FORM_MAIL + """\" method="POST" data-form-id="contacto" data-ok="formOkContact" data-subject="{Nombre} os escribe desde la web · {Motivo}" data-intro="Hola, soy {Nombre}. Os escribo desde la web de la parroquia por este motivo: {Motivo}. Podéis responder a este correo para contestarme directamente[ o llamarme al {Teléfono}]." data-mail-form=\"""" + FORM_MAIL.replace("formsubmit.co/", "formsubmit.co/ajax/") + """\">
                        <div class="form-head">
                            <span class="form-head-icon">""" + SAC_ICONS["mail"] + """</span>
                            <div>
                                <span class="form-head-kicker">Formulario de contacto</span>
                                <strong>Escribe a la parroquia</strong>
                                <small>Consultas, sacramentos, visitas o cualquier otra cosa</small>
                            </div>
                        </div>
                        <input type="hidden" name="Formulario" value="Contacto desde la web">
                        <input type="hidden" name="_subject" value="Nuevo mensaje desde la web">
                        <input type="hidden" name="_template" value="table">
                        <input type="hidden" name="_captcha" value="false">
                        <input type="text" name="_honey" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
                        <fieldset class="motive-picker" data-purpose>
                            <legend class="picker-label">¿En qué te podemos ayudar? *</legend>
                            <div class="chips">
""" + "\n".join(f'''                                <label class="chip"><input type="radio" name="Motivo" value="{v}" data-hint="{h}"{' required' if i == 0 else ''}><span>{t}</span></label>''' for i, (v, t, h) in enumerate(MOTIVOS)) + """
                            </div>
                            <p class="motive-note" data-for="Primera Comunión" hidden>Para inscribir a un niño o una niña tienes un formulario propio: <a href="comuniones.html#inscripcion">inscripción a la Primera Comunión →</a></p>
                        </fieldset>
                        <div class="form-grid">
                            <label>Nombre *<input type="text" name="Nombre" required autocomplete="name"></label>
                            <label>Teléfono<input type="tel" name="Teléfono" autocomplete="tel" inputmode="tel"></label>
                        </div>
                        <label>Correo electrónico *<input type="email" name="Correo electrónico" required autocomplete="email"></label>
                        <label>Mensaje *<textarea name="Mensaje" rows="5" required placeholder="Cuéntanos en qué podemos ayudarte"></textarea></label>
                        <label class="consent"><input type="checkbox" name="Consentimiento" value="Sí, acepto la política de privacidad" required>
                            <span>Acepto la <a href="privacidad.html" target="_blank">política de privacidad</a>. *</span></label>
                        <button type="submit" class="btn btn-solid">Enviar mensaje</button>
                        <p class="form-status" role="status" aria-live="polite"></p>
                    </form>
                    <div class="data-notice">
                        <strong>Información básica sobre protección de datos</strong>
                        <p><b>Responsable:</b> Parroquia de Santa Teresa de Jesús. <b>Finalidad:</b> atender tu consulta. <b>Legitimación:</b> tu consentimiento. <b>Destinatarios:</b> no se ceden datos a terceros, salvo obligación legal; el envío por correo lo gestiona FormSubmit. <b>Derechos:</b> acceso, rectificación, supresión y otros, escribiendo a <a href="mailto:albertsols@gmail.com">albertsols@gmail.com</a>. <a href="privacidad.html">Más información en la Política de privacidad</a>.</p>
                    </div>
                </div>
                <aside class="contact-aside">
                    <span class="subtitulo text-left">¿Prefieres hablar?</span>
                    <h2 class="text-left">Te atendemos</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <a class="contact-call" href=\"tel:""" + TEL + """\">
                        <span class="contact-call-icon">""" + ICON_PHONE + """</span>
                        <span><small>Llamar a la parroquia</small><strong>""" + TEL_TXT + """</strong></span>
                    </a>
                    <ul class="contact-facts">
                        <li>""" + ICON_CLOCK + """<div><strong>Despacho parroquial</strong><span>Viernes por la tarde, y antes o después de cada misa</span></div></li>
                        <li>""" + ICON_PIN + """<div><strong>Carrer del Llobregós, 132</strong><span>08032 Barcelona · El Carmel · <a href="#mapa">ver el mapa ↓</a></span></div></li>
                        <li>""" + SAC_ICONS["mail"].replace('<svg ', '<svg class="icon" ') + """<div><strong>Correo electrónico</strong><span><a href="mailto:albertsols@gmail.com">albertsols@gmail.com</a></span></div></li>
                        <li>""" + SAC_ICONS["insta"].replace('<svg ', '<svg class="icon" ') + """<div><strong>Instagram</strong><span><a href="https://www.instagram.com/p.santateresadejesusbcn/" target="_blank" rel="noopener">@p.santateresadejesusbcn</a></span></div></li>
                    </ul>
                </aside>
            </div>
        </section>
""" + location_block(big=True, sid="mapa") + """
""")

# ---------------------------------------------------------------- MISAS
# Horario semanal de la página de Eucaristías: (día, número del día para resaltar «hoy» [0 = domingo], actos).
# Cada acto: (hora, qué, detalle opcional). El mismo horario está en data/eucaristias.ics para añadirlo al móvil.
WEEK_PLAN = [
    ("Lunes", 1, [("19:00", "Eucaristía", "")]),
    ("Martes", 2, [("19:00", "Eucaristía", "")]),
    ("Miércoles", 3, [("19:00", "Eucaristía", ""), ("19:30", "Adoración al Santísimo", "Media hora con bendición")]),
    ("Jueves", 4, [("19:00", "Eucaristía", "")]),
    ("Viernes", 5, [("19:00", "Eucaristía", ""), ("Tarde", "Despacho parroquial", "Para bautizos, bodas y cualquier consulta")]),
    ("Sábado", 6, [("18:30", "Sacramento del Perdón", "Hasta las 19:00"), ("19:00", "Eucaristía", "")]),
    ("Domingo", 0, [("11:00", "Eucaristía con coro góspel", "Salvo en agosto"), ("13:15", "Eucaristía", "")]),
]


def week_plan():
    rows = []
    for day, idx, items in WEEK_PLAN:
        acts = "".join(
            f'<li><span class="wp-time">{t}</span><span class="wp-what">{w}{f"<small>{d}</small>" if d else ""}</span></li>'
            for t, w, d in items)
        rows.append(f'                        <li class="week-day" data-days="{idx}"><span class="wp-day">{day}</span><ul>{acts}</ul></li>')
    return '<ol class="week-plan">\n' + "\n".join(rows) + "\n                    </ol>"


PAGES["html/misas.html"] = page(1, "Eucaristías", "Horarios de misas y calendario de eucaristías y actividades de la Parroquia Santa Teresa de Jesús.", active="eucaristias", body=page_hero("Celebraciones litúrgicas", "Eucaristías", "eucaristia.jpeg") + """
        <section id="horarios">
            <span class="subtitulo">Horarios</span>
            <h2>Horarios de Eucaristía</h2>
            <div style="text-align:center;"><div class="next-mass light" data-next-mass hidden></div></div>
            <div class="grid-container">
                <div class="card" data-days="1,2,3,4,5">
                    <h3>Laborables</h3>
                    <ul><li>19:00 h — Eucaristía</li></ul>
                </div>
                <div class="card" data-days="6">
                    <h3>Sábados</h3>
                    <ul><li>19:00 h — Eucaristía</li></ul>
                </div>
                <div class="card" data-days="0">
                    <h3>Domingos</h3>
                    <ul><li>11:00 h — Eucaristía</li><li>13:15 h — Eucaristía</li></ul>
                </div>
            </div>
        </section>

        <section class="section-alt" id="gospel">
            <div class="two-col">
                <div>
                    <span class="subtitulo">Con coro góspel</span>
                    <h2>Misa dominical de las 11:00 h</h2>
                    <hr class="section-divider">
                    <div class="prose">
                        <p>De las misas que se celebran en fin de semana, desde el punto de vista de animación, destaca la dominical de las 11:00 h. Todos los domingos, salvo en agosto, canta en la misa un amplio grupo de góspel.</p>
                    </div>
                    """ + cincopa("5053ed90-a7d4-4b43-af71-bfb01383be44", "AwFALeeQzr7a") + """
                </div>
                <div id="calendario">
                    <span class="subtitulo">Semana a semana</span>
                    <h2>Calendario de eucaristías y actividades</h2>
                    <hr class="section-divider">
                    """ + week_plan() + """
                    <p class="week-note">Antes o después de cada misa el párroco atiende a quien lo necesite, también para confesarse. El último domingo de cada mes se visita en casa a los enfermos que lo pidan.</p>
                    <div class="btn-group">
                        <a class="btn btn-solid" href="../data/eucaristias.ics" download>Añadir a mi calendario</a>
                        <a class="btn" href="contacto.html#escribenos">Preguntar un horario</a>
                    </div>
                </div>
            </div>
        </section>
""")

# ---------------------------------------------------------------- PÁGINAS DE CADA SACRAMENTO
# Cada texto va en (castellano, catalán, inglés). El botón principal abre el formulario de
# contacto con ese motivo ya marcado (contacto.html?motivo=...).
SAC_TR = []


def _t(es, ca, en):
    SAC_TR.append((es, ca, en))
    return es


SACRAMENTOS = [
    dict(slug="bautismo", icon="agua", photo="sac-bautismo.jpg",
         credit=_t("Grabado de J. A. Riedel según G. M. Crespi · The Met", "Gravat de J. A. Riedel segons G. M. Crespi · The Met", "Engraving by J. A. Riedel after G. M. Crespi · The Met"), motivo="Bautizo",
         title=_t("Bautismo", "Baptisme", "Baptism"),
         h2=_t("Bautizar a vuestro hijo", "Batejar el vostre fill", "Baptising your child"),
         text=_t("El Bautismo es la puerta de la vida cristiana. En la parroquia hay ceremonias bautismales al mediodía en cualquier domingo del año que se pida.",
                 "El Baptisme és la porta de la vida cristiana. A la parròquia hi ha cerimònies baptismals al migdia qualsevol diumenge de l'any que es demani.",
                 "Baptism is the gateway to Christian life. The parish celebrates baptisms at midday on any Sunday of the year you request."),
         info=[(_t("Cuándo", "Quan", "When"), _t("Cualquier domingo del año, al mediodía", "Qualsevol diumenge de l'any, al migdia", "Any Sunday of the year, at midday")),
               (_t("Cómo pedirlo", "Com demanar-ho", "How to request it"), _t("En el despacho parroquial, los viernes por la tarde, o con el formulario", "Al despatx parroquial, els divendres a la tarda, o amb el formulari", "At the parish office on Friday afternoons, or using the form"))],
         cta=_t("Pedir un bautizo", "Demanar un bateig", "Request a baptism")),
    dict(slug="confirmacion", icon="paloma", photo="sac-confirmacion.jpg",
         credit=_t("Grabado de J. A. Riedel según G. M. Crespi · The Met", "Gravat de J. A. Riedel segons G. M. Crespi · The Met", "Engraving by J. A. Riedel after G. M. Crespi · The Met"), motivo="Confirmación",
         title=_t("Confirmación", "Confirmació", "Confirmation"),
         h2=_t("Confirmar la fe", "Confirmar la fe", "Confirming the faith"),
         text=_t("La Confirmación completa la gracia del Bautismo. Se celebra cada tres años y la catequesis prepara a los adolescentes a partir de los 14 años.",
                 "La Confirmació completa la gràcia del Baptisme. Se celebra cada tres anys i la catequesi prepara els adolescents a partir dels 14 anys.",
                 "Confirmation completes the grace of Baptism. It is celebrated every three years, and catechesis prepares teenagers from the age of 14."),
         info=[(_t("Cuándo", "Quan", "When"), _t("Cada tres años", "Cada tres anys", "Every three years")),
               (_t("Edad", "Edat", "Age"), _t("A partir de los 14 años, con catequesis previa", "A partir dels 14 anys, amb catequesi prèvia", "From 14 years old, after catechesis"))],
         cta=_t("Pedir información", "Demanar informació", "Ask for information")),
    dict(slug="matrimonio", icon="anillos", photo="sac-matrimonio.jpg",
         credit=_t("Grabado de L. Zucchi según G. M. Crespi · The Met", "Gravat de L. Zucchi segons G. M. Crespi · The Met", "Engraving by L. Zucchi after G. M. Crespi · The Met"), motivo="Boda",
         title=_t("Matrimonio", "Matrimoni", "Marriage"),
         h2=_t("Casarse en la parroquia", "Casar-se a la parròquia", "Getting married in the parish"),
         text=_t("Os acompañamos en la preparación de vuestra boda y en cada aniversario. Para empezar, pasad por el despacho parroquial los viernes por la tarde o escribidnos.",
                 "Us acompanyem en la preparació del vostre casament i en cada aniversari. Per començar, passeu pel despatx parroquial els divendres a la tarda o escriviu-nos.",
                 "We accompany you as you prepare your wedding and on every anniversary. To start, visit the parish office on Friday afternoons or write to us."),
         info=[(_t("Despacho parroquial", "Despatx parroquial", "Parish office"), _t("Viernes por la tarde", "Divendres a la tarda", "Friday afternoons")),
               (_t("Aniversarios", "Aniversaris", "Anniversaries"), _t("Bodas de plata, rubí, oro, diamante…", "Noces d'argent, robí, or, diamant…", "Silver, ruby, golden, diamond…"))],
         cta=_t("Preparar una boda", "Preparar un casament", "Plan a wedding")),
    dict(slug="perdon", icon="manos", photo="sac-perdon.jpg",
         credit=_t("Grabado de J. A. Riedel según G. M. Crespi · The Met", "Gravat de J. A. Riedel segons G. M. Crespi · The Met", "Engraving by J. A. Riedel after G. M. Crespi · The Met"), motivo="Sacramento del Perdón",
         title=_t("Perdón", "Perdó", "Confession"),
         h2=_t("El sacramento del Perdón", "El sagrament del Perdó", "The sacrament of Confession"),
         text=_t("Mn. Sols administra el sacramento del Perdón de manera fija los sábados de 18:30 a 19:00 horas y siempre un rato antes de cada misa.",
                 "Mn. Sols administra el sagrament del Perdó de manera fixa els dissabtes de 18:30 a 19:00 hores i sempre una estona abans de cada missa.",
                 "Fr. Sols hears confessions every Saturday from 18:30 to 19:00 and always a while before every Mass."),
         info=[(_t("Sábados", "Dissabtes", "Saturdays"), _t("De 18:30 a 19:00", "De 18:30 a 19:00", "From 18:30 to 19:00")),
               (_t("Cada día", "Cada dia", "Every day"), _t("Un rato antes de cada misa", "Una estona abans de cada missa", "A while before every Mass"))],
         cta=_t("Pedir otro horario", "Demanar un altre horari", "Ask for another time")),
    dict(slug="uncion", icon="oleo", photo="sac-uncion.jpg",
         credit=_t("Grabado de J. A. Riedel según G. M. Crespi · The Met", "Gravat de J. A. Riedel segons G. M. Crespi · The Met", "Engraving by J. A. Riedel after G. M. Crespi · The Met"), motivo="Unción de los enfermos",
         title=_t("Unción de los enfermos", "Unció dels malalts", "Anointing of the Sick"),
         h2=_t("Consuelo y fuerza para los enfermos", "Consol i força per als malalts", "Comfort and strength for the sick"),
         text=_t("La Unción da fuerza y consuelo a los enfermos y a las personas mayores. El párroco va a casa, al hospital o a la residencia.",
                 "La Unció dona força i consol als malalts i a la gent gran. El rector va a casa, a l'hospital o a la residència.",
                 "The Anointing brings strength and comfort to the sick and the elderly. The parish priest visits homes, hospitals and care homes."),
         info=[(_t("Dónde", "On", "Where"), _t("En casa, en el hospital o en la residencia", "A casa, a l'hospital o a la residència", "At home, in hospital or in a care home")),
               (_t("Si es urgente", "Si és urgent", "If it is urgent"), _t("Llamad a la parroquia", "Truqueu a la parròquia", "Call the parish"))],
         cta=_t("Pedir la Unción", "Demanar la Unció", "Request the Anointing")),
]
_t("Sacramento", "Sagrament", "Sacrament")
_t("Otros sacramentos", "Altres sagraments", "Other sacraments")
_t("Llamar a la parroquia", "Trucar a la parròquia", "Call the parish")
_t("Más información &rarr;", "Més informació &rarr;", "More information &rarr;")
for _sc in SACRAMENTOS:
    _t(_sc["title"] + " | Parroquia Santa Teresa de Jesús",
       dict(SAC_TR)[_sc["title"]][0] if False else next(c for e, c, n in SAC_TR if e == _sc["title"]) + " | Parròquia de Santa Teresa de Jesús",
       next(n for e, c, n in SAC_TR if e == _sc["title"]) + " | Santa Teresa de Jesús Parish")
    _t(_sc["text"][:150], next(c for e, c, n in SAC_TR if e == _sc["text"])[:150], next(n for e, c, n in SAC_TR if e == _sc["text"])[:150])
SAC_BY = {x["slug"]: x for x in SACRAMENTOS}


def sacrament_page(sc):
    info = "".join(f"\n                        <li><strong>{k}</strong>{v}</li>" for k, v in sc["info"])
    others = "\n".join(icon_card(o["icon"], o["title"], "", o["slug"] + ".html") for o in SACRAMENTOS if o is not sc)
    body = page_hero("Sacramento", sc["title"], "web/sacramentos-hero.jpg", pos="center 40%") + f"""
        <section class="section-warm">
            <div class="two-col center">
                <figure class="sac-arch">
                    <img src="../fotosdefinitivas/web/{sc["photo"]}" alt="{sc["title"]}" width="900" height="1125" loading="lazy">
                    <span class="sac-medal">{SAC_ICONS[sc["icon"]]}</span>
                    <figcaption class="sac-credit">{sc["credit"]}</figcaption>
                </figure>
                <div>
                    <span class="subtitulo text-left">{sc["title"]}</span>
                    <h2 class="text-left">{sc["h2"]}</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <p>{sc["text"]}</p>
                    <ul class="info-list" style="margin:1.5rem 0 2rem;">{info}
                    </ul>
                    <div class="btn-group">
                        <a href="contacto.html?motivo={sc["motivo"].replace(" ", "%20")}#escribenos" class="btn btn-solid">{sc["cta"]}</a>
                        <a href="tel:{TEL}" class="btn btn-call">{ICON_PHONE}<span>Llamar a la parroquia</span></a>
                    </div>
                </div>
            </div>
        </section>
{ANIV_HTML if sc["slug"] == "matrimonio" else ""}
        <section>
            <div class="section-head">
                <span class="subtitulo">Sacramentos</span>
                <h2>Otros sacramentos</h2>
            </div>
            <div class="icon-grid sac-others">
{others}
            </div>
        </section>
"""
    return page(1, sc["title"], sc["text"][:150], body=body)


ANIV_HTML = """        <section class="section-warm" id="aniversarios">
            <div class="two-col center">
                <div class="framed-img">
                    <img src="../fotosdefinitivas/web/fotobodapepi.jpg" alt="Celebración de un aniversario de boda en la parroquia" loading="lazy">
                </div>
                <div>
                    <span class="subtitulo text-left">Aniversarios de boda</span>
                    <h2 class="text-left">Celebrad vuestras bodas de plata, oro o diamante</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <p>¿Cumplís años de casados? En la parroquia podéis dar gracias a Dios por vuestro matrimonio con una bendición especial durante la eucaristía, acompañados de vuestra familia y de toda la comunidad.</p>
                    <ul class="anniv-list">
                        <li class="plata"><b>25</b><span>Bodas de plata</span></li>
                        <li class="rubi"><b>40</b><span>Bodas de rubí</span></li>
                        <li class="oro"><b>50</b><span>Bodas de oro</span></li>
                        <li class="diamante"><b>60</b><span>Bodas de diamante</span></li>
                    </ul>
                    <p class="caption" style="text-align:left;">Y cualquier otro aniversario que queráis celebrar.</p>
                    <div class="btn-group">
                        <a href="contacto.html?motivo=Aniversario%20de%20boda#escribenos" class="btn btn-solid">Pedir la celebración</a>
                        <a href="tel:""" + TEL + """" class="btn btn-call">""" + ICON_PHONE + """<span>Llamar</span></a>
                    </div>
                </div>
            </div>
        </section>

"""


# ---------------------------------------------------------------- SACRAMENTOS
for _sc in SACRAMENTOS:
    PAGES[f"html/{_sc['slug']}.html"] = sacrament_page(_sc)
PAGES["html/adminsacra.html"] = page(1, "Sacramentos", "Sacramento del Perdón, bautizos, confirmación y despacho parroquial en la Parroquia Santa Teresa de Jesús.", body=page_hero("Administración de", "Sacramentos", "web/sacramentos-hero.jpg", pos="center 40%") + """
        <section>
            <div class="section-head">
                """ + ORNAMENT + """
                <span class="subtitulo">Cuándo y cómo</span>
                <h2>Celebrar los sacramentos</h2>
                <p>Te acompañamos en los momentos más importantes de la vida cristiana.</p>
            </div>
            <div class="icon-grid five">
""" + "\n".join([
    icon_card("manos", "Perdón", "Mn. Sols administra el sacramento del Perdón de manera fija los sábados de 18:30 a 19:00 horas y siempre un rato antes de cada misa.", "perdon.html", "Más información"),
    icon_card("agua", "Bautismo", "Hay ceremonias bautismales al mediodía en cualquier domingo del año que se pida.", "bautismo.html", "Más información"),
    icon_card("paloma", "Confirmación", "Cada tres años se celebra la Confirmación. La catequesis prepara a los adolescentes a partir de los 14 años.", "confirmacion.html", "Más información"),
    icon_card("anillos", "Matrimonio", "Bodas, su preparación y aniversarios de plata, oro o diamante: consulta en el despacho parroquial los viernes por la tarde.", "matrimonio.html", "Más información"),
    icon_card("oleo", "Unción de los enfermos", UNCION_TXT, "uncion.html", "Más información", aid="uncion"),
]) + """
            </div>
        </section>

        <section id="despacho">
            <div class="two-col center">
                <div class="priest-portrait">
                    <img src="../fotosdefinitivas/web/parroco-albert.jpg" alt="Mn. Albert Sols, párroco de Santa Teresa de Jesús" width="640" height="640" loading="lazy">
                    <span class="priest-name">Mn. Albert Sols<small>Párroco</small></span>
                </div>
                <div>
                    <span class="subtitulo text-left">Despacho parroquial</span>
                    <h2 class="text-left">Habla con el párroco</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <p>Los viernes por la tarde y, de hecho, un rato antes o después de todas las misas de la semana, el cura párroco atiende a la gente para cualquier tipo de asuntos: bautizos, bodas, visitas a enfermos o cualquier consulta.</p>
                    <div class="btn-group">
                        <a href="catequesis.html" class="btn">Catequesis</a>
                        <a href="misas.html" class="btn">Horarios de misa</a>
                    </div>
                </div>
            </div>
        </section>
""")

# ---------------------------------------------------------------- CATEQUESIS
PAGES["html/catequesis.html"] = page(1, "Catequesis", "Inscripciones a la catequesis de primera comunión y confirmación en la Parroquia Santa Teresa de Jesús.", body=page_hero("Primera comunión y confirmación", "Catequesis", "web/dsc_0448.jpg") + """
        <section>
            <div class="section-head">
                <span class="subtitulo">Formación cristiana</span>
                <h2>Catequesis</h2>
                <hr class="section-divider" style="margin-bottom:1.25rem;">
                <p>Niños y adolescentes reciben, de forma periódica, una formación cristiana que les prepara para recibir el sacramento de la eucaristía y el de la confirmación.</p>
            </div>
            <div class="icon-grid two">
""" + "\n".join([
    icon_card("caliz", "Primera comunión", "Preparación de los niños para recibir por primera vez el sacramento de la eucaristía.", "comuniones.html", "Información e inscripción"),
    icon_card("paloma", "Confirmación", "Para adolescentes a partir de los 14 años. Cada tres años se celebra la Confirmación en la parroquia.", "confirmacion.html", "Más información"),
]) + """
            </div>
        </section>

        <section class="section-warm">
            <a class="family-entry" href="comuniones.html#inscripcion">
                <span class="family-entry-img" style="background-image:url('../fotosdefinitivas/web/dsc_0546.jpg')" aria-hidden="true"></span>
                <span class="family-entry-body">
                    <span class="subtitulo">Inscripciones abiertas</span>
                    <strong>Primera Comunión</strong>
                    <span class="family-entry-text">Rellena la inscripción en línea en un par de minutos: llega directamente a la parroquia y os llamaremos para empezar.</span>
                    <span class="btn btn-solid">Inscribirse a la Primera Comunión</span>
                </span>
            </a>
        </section>
""")

# ---------------------------------------------------------------- PRIMERA COMUNIÓN
# El formulario se envía por correo a la parroquia a través de FormSubmit (sin cuentas ni claves).
# La primera vez que alguien lo use, FormSubmit envía a ese correo un mensaje para ACTIVARLO.
PAGES["html/comuniones.html"] = page(1, "Primera Comunión", "Preparación e inscripción a la Primera Comunión en la Parroquia Santa Teresa de Jesús (El Carmel, Barcelona).", active="eucaristias", body=page_hero("Catequesis de infancia", "Primera Comunión", "web/dsc_0546.jpg", "Primera Comunión") + """
        <section>
            <div class="section-head">
                <span class="subtitulo">Un paso muy especial</span>
                <h2>Preparamos juntos la Primera Comunión</h2>
                <hr class="section-divider" style="margin-bottom:1.25rem;">
                <p>Durante el curso, los niños y niñas se preparan en la catequesis de la parroquia para recibir por primera vez a Jesús en la Eucaristía, acompañados por sus catequistas y por sus familias.</p>
            </div>
            <ol class="communion-steps">
                <li>""" + SAC_ICONS["caliz"] + """<strong>Inscripción</strong><span>Rellenad el formulario de esta página.</span></li>
                <li>""" + ICON_PHONE + """<strong>Os llamamos</strong><span>La parroquia se pone en contacto con la familia.</span></li>
                <li>""" + SAC_ICONS["paloma"] + """<strong>Catequesis</strong><span>Encuentros periódicos durante el curso.</span></li>
                <li>""" + ICON_CROSS + """<strong>Celebración</strong><span>La Primera Comunión, en familia y en comunidad.</span></li>
            </ol>
        </section>

        <section class="section-warm" id="inscripcion">
            <div class="section-head" style="margin-bottom:2rem;">
                <span class="subtitulo">Inscripciones</span>
                <h2>Inscripción a la Primera Comunión</h2>
                <hr class="section-divider" style="margin-bottom:1rem;">
                <p>La inscripción llega directamente por correo a la parroquia. Los campos con * son obligatorios.</p>
            </div>
            <form class="mail-form form-communion" action=\"""" + FORM_MAIL + """\" method="POST" data-form-id="comuniones" data-subject="Inscripción a la Primera Comunión · {Nombre del niño o niña} {Apellidos}" data-intro="Hola, soy {Padre, madre o tutor}. Nos gustaría inscribir a {Nombre del niño o niña} {Apellidos} en la catequesis de Primera Comunión[ (curso: {Curso escolar})]. Aquí tenéis todos los datos. Podéis responder a este correo para contestarnos directamente[ o llamarnos al {Teléfono}]." data-mail-form=\"""" + FORM_MAIL.replace("formsubmit.co/", "formsubmit.co/ajax/") + """\">
                <div class="form-head">
                    <span class="form-head-icon">""" + SAC_ICONS["caliz"] + """</span>
                    <div>
                        <span class="form-head-kicker">Formulario de inscripción</span>
                        <strong>Primera Comunión</strong>
                        <small>Para inscribir a un niño o una niña en la catequesis de Primera Comunión</small>
                    </div>
                </div>
                <input type="hidden" name="Formulario" value="Inscripción a la Primera Comunión">
                <input type="hidden" name="_subject" value="Nueva inscripción a la Primera Comunión">
                <input type="hidden" name="_template" value="table">
                <input type="hidden" name="_captcha" value="false">
                <input type="text" name="_honey" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
                <fieldset>
                    <legend>Datos del niño o de la niña</legend>
                    <div class="form-grid">
                        <label>Nombre *<input type="text" name="Nombre del niño o niña" required autocomplete="off"></label>
                        <label>Apellidos *<input type="text" name="Apellidos" required autocomplete="off"></label>
                        <label>Fecha de nacimiento *<input type="date" name="Fecha de nacimiento" required></label>
                    </div>
                    <fieldset class="motive-picker compact" data-purpose>
                        <legend class="picker-label">Curso escolar</legend>
                        <div class="chips">
                            <label class="chip"><input type="radio" name="Curso escolar" value="2º de Primaria"><span>2º Primaria</span></label>
                            <label class="chip"><input type="radio" name="Curso escolar" value="3º de Primaria"><span>3º Primaria</span></label>
                            <label class="chip"><input type="radio" name="Curso escolar" value="4º de Primaria"><span>4º Primaria</span></label>
                            <label class="chip"><input type="radio" name="Curso escolar" value="5º de Primaria"><span>5º Primaria</span></label>
                            <label class="chip"><input type="radio" name="Curso escolar" value="6º de Primaria"><span>6º Primaria</span></label>
                            <label class="chip"><input type="radio" name="Curso escolar" value="Otro"><span>Otro</span></label>
                        </div>
                    </fieldset>
                    <fieldset class="motive-picker compact">
                        <legend class="picker-label">¿Está bautizado o bautizada? *</legend>
                        <div class="chips">
                            <label class="chip"><input type="radio" name="Bautizado/a" value="Sí" required><span>Sí</span></label>
                            <label class="chip"><input type="radio" name="Bautizado/a" value="No"><span>No</span></label>
                            <label class="chip"><input type="radio" name="Bautizado/a" value="No lo sé"><span>No lo sé</span></label>
                        </div>
                    </fieldset>
                    <label>Parroquia donde fue bautizado/a<input type="text" name="Parroquia de bautismo" placeholder="Si lo sabéis"></label>
                </fieldset>
                <fieldset>
                    <legend>Datos de la familia</legend>
                    <div class="form-grid">
                        <label>Nombre del padre, madre o tutor *<input type="text" name="Padre, madre o tutor" required autocomplete="name"></label>
                        <label>Teléfono *<input type="tel" name="Teléfono" required autocomplete="tel" inputmode="tel"></label>
                    </div>
                    <label>Correo electrónico *<input type="email" name="Correo electrónico" required autocomplete="email"></label>
                    <label>Observaciones<textarea name="Observaciones" rows="4" placeholder="Alergias, necesidades especiales, horarios que os van mejor…"></textarea></label>
                </fieldset>
                <label class="consent"><input type="checkbox" name="Consentimiento" value="Sí, soy el padre, la madre o el tutor legal y acepto la política de privacidad" required>
                    <span>Soy el padre, la madre o el tutor legal y acepto la <a href="privacidad.html" target="_blank">política de privacidad</a>. *</span></label>
                <button type="submit" class="btn btn-solid">Enviar inscripción</button>
                <p class="form-status" role="status" aria-live="polite"></p>
            </form>
            <div class="data-notice" style="max-width:820px; margin:1.5rem auto 0;">
                <strong>Información básica sobre protección de datos</strong>
                <p><b>Responsable:</b> Parroquia de Santa Teresa de Jesús. <b>Finalidad:</b> gestionar la inscripción y la preparación a la Primera Comunión. <b>Legitimación:</b> consentimiento del padre, madre o tutor legal (los datos de menores de 14 años solo pueden facilitarlos ellos). <b>Destinatarios:</b> no se ceden a terceros, salvo obligación legal; el envío por correo lo gestiona FormSubmit. <b>Derechos:</b> acceso, rectificación, supresión y otros, escribiendo a <a href="mailto:albertsols@gmail.com">albertsols@gmail.com</a>. <a href="privacidad.html">Más información en la Política de privacidad</a>.</p>
            </div>
            <p class="form-alt">¿Prefieres hacerlo por teléfono? <a href=\"tel:""" + TEL + """\" class="tel-link"><b>""" + TEL_TXT + """</b></a></p>
        </section>
""")

# ---------------------------------------------------------------- IMÁGENES
PAGES["html/imagenes.html"] = page(1, "Imágenes y vídeos", "Vídeos y álbumes fotográficos de la Parroquia Santa Teresa de Jesús de Barcelona.", body=page_hero("Galería", "Imágenes y Vídeos", "web/portada2.jpg") + """
        <section class="section-warm">
            <div class="section-head">
                <span class="subtitulo">Nuestra parroquia</span>
                <h2>Galería de fotos</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
""" + mosaic(GALLERY + [
    ("dsc_0546.jpg", "La iglesia llena durante una celebración", "wide"),
    ("dsc_0591.jpg", "Domingo de Ramos en el patio", ""),
    ("img_5493.jpg", "Capilla del Santísimo", ""),
], 1) + """
        </section>

        <section>
            <div class="two-col">
                <div>
                    <span class="subtitulo">Vídeos</span>
                    <h2>Nuestros últimos vídeos</h2>
                    <hr class="section-divider">
                    <div class="embed-16x9">
                        <iframe title="Vídeo de la parroquia" src="https://www.youtube-nocookie.com/embed/nMkDxLVOVzA" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </div>
                    <div class="embed-16x9">
                        <iframe title="Vídeo de la parroquia" src="https://www.youtube-nocookie.com/embed/_vj1fue9nnY" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </div>
                </div>
                <div>
                    <span class="subtitulo">Fotografías</span>
                    <h2>Álbumes fotográficos</h2>
                    <hr class="section-divider">
                    <div class="btn-stack">
                        <a href="https://drive.google.com/drive/folders/1jfgSnLel08doU2DFm9UpX_9xhO_O8ZT-?usp=sharing" class="btn" target="_blank" rel="noopener">Fotografías de las comuniones 2021</a>
                    </div>
                    """ + cincopa("7e90e2d4-db4c-443c-9da2-f0eae76a49a0", "AUKA6f-1tvEd") + """
                </div>
            </div>
        </section>
""")

# ---------------------------------------------------------------- HOMILÍAS (desde el panel)
def reading_audio(src):
    return f"""                <div class="reading-audio">
                    <span class="reading-audio-label"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/></svg>Escuchar la reflexión</span>
                    <iframe title="Audio de la reflexión" width="100%" height="120" scrolling="no" frameborder="no" loading="lazy" src="{src}"></iframe>
                </div>"""


def homily_page(i, h):
    newer = HOMILIAS[i - 1] if i > 0 else None
    older = HOMILIAS[i + 1] if i + 1 < len(HOMILIAS) else None
    audio = reading_audio(HOM.audio_src(h.get("audio"))) if h.get("audio") else ""
    pres = (f"""
                <div class="btn-group center reading-actions">
                    <a class="btn" href="{esc(h["presentacion"])}" target="_blank" rel="noopener">Descarga la presentación &raquo;</a>
                </div>""" if h.get("presentacion") else "")
    saludo = f'\n                    <p class="lead">{esc(h["saludo"])}</p>' if h.get("saludo") else ""

    def nav_card(o, rel_label):
        return f"""
                    <a class="reading-next" href="{o["slug"]}.html" style="--author:{o["autor_color"]}">
                        {_portrait(o, 2, "reading-next-photo")}
                        <div class="reading-next-text"><span class="book-kicker">{rel_label}</span><strong>{esc(o["titulo"])}</strong><p><span>{esc(o["autor_nombre"])}</span> · {date_long(o)}</p></div>
                        <span class="reading-arrow" aria-hidden="true">&rarr;</span>
                    </a>"""
    cards = ""
    if newer:
        cards += nav_card(newer, "Reflexión más reciente")
    if older:
        cards += nav_card(older, "Reflexión anterior")
    other = ""
    if cards:
        other = f"""
                <nav class="reading-nav" aria-label="Otras reflexiones">
                    <span class="subtitulo">Sigue leyendo</span>{cards}
                    <a class="link-arrow" href="../humiliasmenu.html">Ver todas las reflexiones <span>&rarr;</span></a>
                </nav>"""
    desc = f"{h['titulo']} — reflexión de {h['autor_nombre']} en la Parroquia Santa Teresa de Jesús."
    eyebrow = esc(h["kicker"]) if h["kicker"] else date_long(h)
    body = page_hero(eyebrow, esc(h["titulo"]), crumb="Homilías").replace('href="../index.html"', 'href="../../index.html"').replace("url('../fotosdefinitivas/", "url('../../fotosdefinitivas/") + f"""
        <section class="reading">
            <div class="reading-wrap">
                <div class="reading-author">
                    {_portrait(h, 2)}
                    <div class="reading-author-text">
                        <span class="book-kicker">{esc(h["autor_cargo"])}</span>
                        <strong>{esc(h["autor_nombre"])}</strong>
                        <span class="reading-date">{date_long(h)}</span>
                    </div>
                </div>
{audio}{pres}
                <article class="prose book-page reading-book">
                    <div class="reading-head">
                        <span class="book-kicker">{esc(h["kicker"])}</span>
                        {date_badge(h)}
                    </div>
                    <h2 class="reading-title">{esc(h["titulo"])}</h2>
                    {ORNAMENT}{saludo}
{HOM.markdown(h.get("texto", ""))}
                    <p class="firma">{esc(h["autor_nombre"])}</p>
                </article>
{other}
            </div>
        </section>
"""
    return page(2, esc(h["titulo"]), esc(desc), body=body, active="noticias")


for _i, _h in enumerate(HOMILIAS):
    PAGES[_h["url"]] = homily_page(_i, _h)

# ---------------------------------------------------------------- NOTICIAS DE LA PARROQUIA
# Se escriben en el panel (colección «Noticias de la parroquia», carpeta contenido/noticias).
# Páginas: html/noticias-parroquia.html (todas) y html/noticias/<fecha-titulo>.html (cada una).
import glob as _glob


def _load_news():
    out = []
    for path in sorted(_glob.glob(os.path.join(ROOT, "contenido", "noticias", "*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                n = _json.load(fh) or {}
        except ValueError as e:
            print("AVISO: no se pudo leer", os.path.basename(path), e)
            continue
        if not (n.get("titulo") or "").strip() or n.get("publicado") is False:
            continue
        slug = os.path.splitext(os.path.basename(path))[0]
        n.update(slug=slug, url=f"html/noticias/{slug}.html", fecha=(n.get("fecha") or "")[:10],
                 foto=REV.media(ROOT, n.get("foto")), enlace=(n.get("enlace") or "").strip(),
                 extracto=(n.get("resumen") or "").strip() or HOM.first_paragraph(n.get("texto", "")))
        out.append(n)
    return sorted(out, key=lambda n: n["fecha"], reverse=True)


NEWS = _load_news()


def news_card(n, depth):
    root = "../" * depth
    img = rev_img(n["foto"], depth, 640) if n["foto"] else f'<span class="rv-card-mark">{LOGO_MARK}</span>'
    return f"""
                <a class="rv-card pn-card" href="{root}{n["url"]}">
                    <span class="rv-card-img{'' if n['foto'] else ' is-empty'}">{img}</span>
                    <span class="rv-card-body">
                        {date_long(n, "pn-date")}
                        <strong>{esc(n["titulo"])}</strong>
                        {f'<span class="rv-card-text">{esc(n["extracto"])}</span>' if n["extracto"] else ""}
                    </span>
                </a>"""


def news_list_page():
    if NEWS:
        grid = f'<div class="rv-cards">{"".join(news_card(n, 1) for n in NEWS)}\n            </div>'
    else:
        grid = '<p class="lead" style="text-align:center;">Muy pronto publicaremos aquí las noticias de la parroquia.</p>'
    body = page_hero("Actualidad", "Noticias de la parroquia", "web/dsc_0586.jpg") + f"""
        <section>
            <div class="section-head">
                <span class="subtitulo">De nuestra parroquia</span>
                <h2>Lo que pasa en Santa Teresa</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            {grid}
            <div class="btn-group center" style="margin-top:2.5rem;">
                <a class="btn" href="{IG_URL}" target="_blank" rel="noopener">Más en nuestro Instagram</a>
                <a class="btn" href="noticias.html#actualidad-iglesia">Noticias de la Iglesia</a>
            </div>
        </section>
"""
    return page(1, "Noticias de la parroquia", "Noticias de la Parroquia Santa Teresa de Jesús, en el barrio del Carmel (Barcelona).", body=body, active="noticias")


def news_page(i, n):
    figure = ""
    if n["foto"]:
        cap = f"\n                        <figcaption>{esc(n['pie'])}</figcaption>" if (n.get("pie") or "").strip() else ""
        figure = f"""
                    <figure class="rv-figure">
                        {rev_img(n["foto"], 2, 1100, n.get("pie") or n["titulo"], lazy=False)}{cap}
                    </figure>"""
    lead = f'\n                    <p class="lead rv-lead">{esc(n["resumen"])}</p>' if (n.get("resumen") or "").strip() else ""
    more = f'\n                    <p class="btn-group"><a class="btn" href="{esc(n["enlace"])}" target="_blank" rel="noopener">Más información</a></p>' if n["enlace"] else ""
    others = [o for o in NEWS if o is not n][:3]
    other_cards = f"""
        <section class="section-alt">
            <div class="section-head">
                <span class="subtitulo">Sigue leyendo</span>
                <h2>Más noticias de la parroquia</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="rv-cards">{"".join(news_card(o, 2) for o in others)}
            </div>
        </section>
""" if others else ""
    body = _hero2("Noticias de la parroquia", esc(n["titulo"]), "Noticias", "web/dsc_0586.jpg") + f"""
        <section class="reading">
            <div class="reading-wrap">
                <a class="rv-back" href="../noticias-parroquia.html">&larr; <span>Todas las noticias de la parroquia</span></a>
                <article class="prose book-page reading-book rv-article">
                    <div class="reading-head">
                        <span class="book-kicker">Noticias de la parroquia</span>
                        {date_long(n, "rv-issue-tag")}
                    </div>
                    <h2 class="reading-title">{esc(n["titulo"])}</h2>
                    {ORNAMENT}{lead}{figure}
{HOM.markdown(n.get("texto", ""))}{more}
                </article>
            </div>
        </section>
""" + other_cards
    desc = (n["extracto"] or n["titulo"])[:180]
    return rev_og(page(2, qesc(n["titulo"]), qesc(desc), body=body, active="noticias"), n["foto"])


PAGES["html/noticias-parroquia.html"] = news_list_page()
for _i, _n in enumerate(NEWS):
    PAGES[_n["url"]] = news_page(_i, _n)

# ---------------------------------------------------------------- BUSCADOR DE PARROQUIAS
# El buscador del Arzobispado, dentro de nuestra web (se carga cuando se acepta el contenido externo)
PAGES["html/buscador-parroquias.html"] = page(1, "Buscar una parroquia", "Encuentra cualquier parroquia de la archidiócesis de Barcelona sin salir de la web de la Parroquia Santa Teresa de Jesús.", active="buscador", body=page_hero("Archidiócesis de Barcelona", "Buscar una parroquia", "web/dsc_0541.jpg") + """
        <section>
            <div class="section-head">
                <span class="subtitulo">Buscador de parroquias</span>
                <h2>Todas las parroquias de Barcelona</h2>
                <hr class="section-divider" style="margin-bottom:1.25rem;">
                <p>Busca por nombre, barrio o población con el buscador oficial del Arzobispado de Barcelona, aquí mismo.</p>
            </div>
            <div class="finder-frame">
                <iframe title="Buscador de parroquias del Arzobispado de Barcelona" src="https://esglesia.barcelona/es/parroquia/" height="1100" loading="lazy"></iframe>
            </div>
            <div class="finder-own">
                <span class="finder-own-mark">""" + LOGO_MARK + """</span>
                <div>
                    <strong>Parroquia Santa Teresa de Jesús</strong>
                    <span>Carrer del Llobregós, 132 · 08032 Barcelona · El Carmel</span>
                </div>
                <a class="btn btn-solid" href="contacto.html#mapa">Cómo llegar</a>
            </div>
        </section>
""")

# Revista digital: página general, una por número y una por artículo
if REVISTA_ON or REV_ISSUES:
    PAGES["html/revista.html"] = revista_archive_page()
for _i, _n in enumerate(REV_ISSUES):
    PAGES[_n["url"]] = revista_issue_page(_i, _n)
    for _j, _a in enumerate(_n["articulos"]):
        PAGES[_a["url"]] = revista_article_page(_n, _j, _a)


def archive_body():
    if not HOMILIAS:
        return ""
    top = HOMILIAS[0]
    quote = _first_quote(top.get("texto"))
    featured = f"""
            <article class="reflection-featured" style="--author:{top["autor_color"]}">
                <a class="rf-photo" href="reflexiones/{top["slug"]}.html" aria-hidden="true" tabindex="-1">
                    {_portrait(top, 1)}
                    {date_badge(top)}
                </a>
                <div class="rf-body">
                    <span class="rf-tag"><span class="notice-dot" aria-hidden="true"></span>Última reflexión</span>{new_badge(top)}
                    <span class="book-kicker">{esc(top["kicker"])}</span>
                    <h3><a href="reflexiones/{top["slug"]}.html">{esc(top["titulo"])}</a></h3>
                    <p class="rf-meta"><strong>{esc(top["autor_nombre"])}</strong> · {date_long(top)}</p>
                    {f'<blockquote class="rf-quote">{esc(quote)}</blockquote>' if quote else f'<p class="rf-excerpt">{esc(top["extracto"])}</p>'}
                    <div class="btn-group">
                        <a class="btn btn-solid" href="reflexiones/{top["slug"]}.html">Leer la reflexión</a>
                        {'<span class="rf-audio">🎧 Con audio</span>' if top.get("audio") else ''}
                    </div>
                </div>
            </article>"""
    autores = []
    for h in HOMILIAS:
        if h["autor_nombre"] not in autores:
            autores.append(h["autor_nombre"])
    filters = ""
    if len(autores) > 1 and len(HOMILIAS) > 2:
        filters = ('<div class="news-filters rf-filters" role="group" aria-label="Filtrar por autor">'
                   '<button type="button" data-author="" aria-pressed="true">Todas</button>' +
                   "".join(f'<button type="button" data-author="{esc(a)}" aria-pressed="false">{esc(a)}</button>' for a in autores) +
                   "</div>")
    rows, year = [], None
    for h in HOMILIAS[1:]:
        y = h["fecha"][:4]
        if y != year:
            year = y
            rows.append(f'<li class="rf-year" aria-hidden="true"><span>{y}</span></li>')
        rows.append(f"""
                <li class="rf-row" data-author="{esc(h["autor_nombre"])}" style="--author:{h["autor_color"]}">
                    <a href="reflexiones/{h["slug"]}.html">
                        {date_badge(h)}
                        {_portrait(h, 1, "rf-avatar")}
                        <span class="rf-text">
                            <span class="book-kicker">{esc(h["kicker"])}</span>
                            <strong>{esc(h["titulo"])}</strong>
                            <em>{esc(h["autor_nombre"])}</em>
                        </span>
                        <span class="reading-arrow" aria-hidden="true">&rarr;</span>
                    </a>
                </li>""")
    older = ""
    if rows:
        older = f"""
            <div class="section-head rf-older-head">
                <span class="subtitulo">Historial</span>
                <h2>Reflexiones anteriores</h2>
                <hr class="section-divider" style="margin-bottom:1.25rem;">
                {filters}
            </div>
            <ol class="rf-list">{"".join(rows)}
            </ol>"""
    return featured + older


PAGES["html/humiliasmenu.html"] = page(1, "Reflexiones", "Reflexiones y comentarios del Evangelio de la Parroquia Santa Teresa de Jesús.", active="noticias", body=page_hero("De nuestra parroquia", "Reflexiones del Evangelio", crumb="Homilías") + """
        <section class="reading reflections-archive">""" + archive_body() + """
        </section>
""")

# ---------------------------------------------------------------- JÓVENES
PAGES["html/jovenes2alternativa.html"] = page(1, "Jóvenes", "Grupo de jóvenes de la Parroquia Santa Teresa de Jesús de Barcelona. ¿Te gustaría formar parte?", body=page_hero("Hola, bienvenido", "Jóvenes Santa Teresa", "web/img_5495.jpg", "Jóvenes") + """
        <section>
            <div class="prose" style="text-align:center;">
                <span class="subtitulo">Equipo de jóvenes</span>
                <h2>¿Te gustaría formar parte de nuestro grupo?</h2>
                <hr class="section-divider">
                <p style="text-align:center;">Cada 8 sábados aproximadamente, un pequeño grupo de jóvenes, acompañados de algún matrimonio, comentan con el rector el evangelio del domingo.</p>
                <p class="lead" style="text-align:center;">¿Quieres formar parte de nuestro club? ¿Todavía lo estás pensando?</p>
                <div class="btn-group center">
                    <a href="contacto.html?motivo=Grupo%20de%20jóvenes#escribenos" class="btn btn-solid">Quiero apuntarme</a>
                    <a href="https://www.instagram.com/p.santateresadejesusbcn/" class="btn" target="_blank" rel="noopener">Síguenos en Instagram</a>
                </div>
            </div>
        </section>

        <section class="section-alt">
            <div class="media-frame" style="max-width:900px; margin:0 auto;">
                <img src="""+img("IMG_5495.jpg")+""" alt="Equipo de jóvenes de la parroquia" loading="lazy">
            </div>
        </section>
""")

# ---------------------------------------------------------------- NOTICIAS

PAGES["html/noticias.html"] = page(1, "Noticias", "Noticias de la Parroquia Santa Teresa de Jesús, del Vaticano y del Arzobispado de Barcelona.", active="noticias", extra_head=NEWS_HEAD_1, body=page_hero("Actualidad de la Iglesia", "Noticias", "web/dsc_0541.jpg") + f"""
        <section id="parroquia" class="parish-news">""" + ("" if not NEWS else f"""
            <div class="section-head pn-latest-head">
                <span class="subtitulo">Noticias de nuestra parroquia</span>
                <h2>Últimas noticias</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="rv-cards pn-latest">{"".join(news_card(n, 1) for n in NEWS[:3])}
            </div>
            <div class="btn-group center" style="margin:2rem 0 4rem;"><a class="btn btn-solid" href="noticias-parroquia.html">Todas las noticias de la parroquia</a></div>""") + f"""
            <div class="parish-news-grid">
                <div class="parish-news-text">
                    <span class="subtitulo">Noticias de nuestra parroquia</span>
                    <h2>Lo más reciente, en nuestro Instagram</h2>
                    <hr class="section-divider left">
                    <p class="lead">Las noticias más recientes de la parroquia —celebraciones, actividades, avisos y fotos de la comunidad— las publicamos en nuestro perfil de Instagram.</p>
                    <ul class="parish-news-list">
                        <li>Avisos y horarios especiales</li>
                        <li>Fotos de las celebraciones y fiestas</li>
                        <li>Actividades de catequesis, jóvenes y Cáritas</li>
                    </ul>
                    <a class="ig-handle" href="{IG_URL}" target="_blank" rel="noopener">{ICON_IG}<span>@p.santateresadejesusbcn</span></a>
                    <div class="btn-group">
                        <a class="btn btn-solid" href="{IG_URL}" target="_blank" rel="noopener">Seguir en Instagram</a>
                        <a class="btn" href="#actualidad-iglesia">Noticias de la Iglesia</a>
                    </div>
                </div>
                <div class="ig-phone" aria-label="Vista previa de nuestro Instagram">
                    <div class="ig-phone-top">
                        <img src="../fotosdefinitivas/web/santateresa-retrato.jpg" alt="" loading="lazy">
                        <div><strong>p.santateresadejesusbcn</strong><span>Parroquia Santa Teresa de Jesús · Barcelona</span></div>
                        <a href="{IG_URL}" target="_blank" rel="noopener">Seguir</a>
                    </div>
                    <div class="ig-phone-feed">
                        {ig_grid(1)}
                        <a class="ig-feed-more" href="{IG_URL}" target="_blank" rel="noopener">Ver todas las publicaciones</a>
                    </div>
                </div>
            </div>
        </section>

        <div id="actualidad-iglesia" class="section-head news-church-head">
            <span class="subtitulo">Actualidad de la Iglesia</span>
            <h2>Vaticano y Arzobispado de Barcelona</h2>
            <hr class="section-divider" style="margin-bottom:0;">
        </div>
""" + """
        <section class="news-page">
            <div class="news-toolbar">
                <div class="news-filters" role="group" aria-label="Filtrar noticias">
                    <button type="button" data-filter="all" aria-pressed="true">Todas</button>
                    <button type="button" data-filter="vaticano" aria-pressed="false"><span class="dot vatican"></span>Vaticano</button>
                    <button type="button" data-filter="arzobispado" aria-pressed="false"><span class="dot diocese"></span>Arzobispado de Barcelona</button>
                </div>
                <p class="news-updated" data-news-updated></p>
            </div>
            <div class="news-photos-notice">
                <p>Las fotos de las noticias se cargan desde Vatican News y el Arzobispado de Barcelona.</p>
                <button type="button" class="btn btn-solid" data-consent-accept>Mostrar fotos</button>
            </div>
            <div class="news-board" data-news-page><p class="news-empty">Cargando noticias…</p></div>
            <div class="news-sources">
                <a href="https://www.vaticannews.va/es.html" target="_blank" rel="noopener" class="news-source-card vatican">
                    <span class="news-badge vatican">Santa Sede</span>
                    <strong>Vatican News</strong>
                    <span>Todas las noticias del Papa y de la Santa Sede &rarr;</span>
                </a>
                <a href="https://esglesia.barcelona/es/" target="_blank" rel="noopener" class="news-source-card diocese">
                    <span class="news-badge diocese">Diócesis</span>
                    <strong>Arzobispado de Barcelona</strong>
                    <span>Actualidad de la Iglesia en Barcelona &rarr;</span>
                </a>
            </div>
        </section>

        <section class="section-warm" id="homilias">
            <div class="section-head" style="margin-bottom:2.5rem;">
                <span class="subtitulo">De nuestra parroquia</span>
                <h2>Reflexiones y homilías</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="reflection-list news-reflections">""" + "".join(f"""
                <a class="reflection-card" href="reflexiones/{h["slug"]}.html" style="--author:{h["autor_color"]}">
                    {_portrait(h, 1)}
                    {new_badge(h)}
                    <span class="book-kicker">{esc(h["autor_nombre"])}</span>
                    <h3>{esc(h["titulo"])}</h3>
                    <span class="reflection-date">{date_long(h)}</span>
                    <span class="flip-hint">Leer &rarr;</span>
                </a>""" for h in HOMILIAS[:6]) + """
            </div>
            <div class="btn-group center" style="margin-top:2.5rem;">
                <a href="humiliasmenu.html" class="btn btn-solid">Ver todas las reflexiones</a>
            </div>
        </section>
""")

# ---------------------------------------------------------------- EVANGELIO PARA LA FAMILIA
# Se inserta la página de evangeli.net tal cual (ellos ofrecen ponerla en otras webs). En catalán
# e inglés se cambia la dirección por su versión en ese idioma (ver FAMILY_URL más abajo).
FAMILY_URL = "https://family.evangeli.net/es"
PAGES["html/evangelio-familia.html"] = page(1, "El Evangelio para la familia", "El Evangelio de cada día explicado para leerlo en familia: texto, comentario, ilustración y juegos para los niños.", active="familia", body=page_hero("Para leer en casa", "El Evangelio para la familia", "web/familia-pixelada.jpg", "Evangelio para la familia", "center 30%") + """
        <section class="section-warm">
            <div class="family-intro">
                <div>
                    <span class="subtitulo text-left">Cada día, una página nueva</span>
                    <h2 class="text-left">La Palabra de Dios, al alcance de los más pequeños</h2>
                    <hr class="section-divider left">
                    <p class="lead">evangeli.net prepara cada día el Evangelio pensado para la familia: el texto del día, un comentario sencillo, una ilustración y juegos para los niños.</p>
                    <p>Os lo ofrecemos aquí para que podáis leerlo juntos en casa, en la mesa o antes de dormir.</p>
                </div>
                <ol class="family-steps">
                    <li><strong>Leed el Evangelio</strong><span>En voz alta, despacio, todos juntos.</span></li>
                    <li><strong>Mirad la ilustración</strong><span>¿Qué personajes aparecen? ¿Qué está pasando?</span></li>
                    <li><strong>Comentadlo en familia</strong><span>¿Qué nos dice Jesús hoy a cada uno?</span></li>
                    <li><strong>Jugad y rezad</strong><span>Haced el puzzle o el juego del día y terminad con una oración.</span></li>
                </ol>
            </div>
        </section>

        <section id="evangelio-familia">
            <div class="section-head" style="margin-bottom:2.5rem;">
                <span class="subtitulo">evangeli.net</span>
                <h2>El Evangelio de hoy para la familia</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="family-frame">
                <div class="family-frame-bar"><i></i><i></i><i></i><span>family.evangeli.net</span><a href=\"""" + FAMILY_URL + """\" target="_blank" rel="noopener">Abrir en evangeli.net <span>&rarr;</span></a></div>
                <iframe title="El Evangelio de hoy para la familia" loading="lazy" src=\"""" + FAMILY_URL + """\"></iframe>
            </div>
            <p class="family-note">Contenido de evangeli.net (Associació Cultural M&amp;M Euroeditors), que se actualiza cada día.</p>
        </section>
""")

# ---------------------------------------------------------------- COOKIES
PAGES["html/cookies.html"] = page(1, "Política de cookies", "Qué cookies utiliza la web de la Parroquia Santa Teresa de Jesús y cómo gestionarlas.", cta=False, body=page_hero("Información legal", "Política de Cookies", crumb="Cookies") + """
        <section>
            <article class="prose legal">
                <p class="updated">Última actualización: """ + LEGAL["actualizado"] + """</p>

                <h3>¿Qué son las cookies?</h3>
                <p>Las cookies y tecnologías similares (como el almacenamiento local del navegador) son pequeños archivos que una web guarda en tu dispositivo para recordar información sobre tu visita.</p>

                <h3>Cookies que utiliza esta web</h3>
                <p>Esta web <strong>no utiliza cookies propias de publicidad ni de analítica</strong>. Solo usa:</p>

                <h4>1. Técnicas y necesarias (no requieren consentimiento)</h4>
                <div class="table-wrap"><table>
                    <thead><tr><th>Nombre</th><th>Titular</th><th>Finalidad</th><th>Duración</th></tr></thead>
                    <tbody>
                        <tr><td>pst-consent</td><td>Propia (almacenamiento local)</td><td>Recordar tus preferencias de cookies.</td><td>12 meses</td></tr>
                        <tr><td>pst-aviso-*</td><td>Propia (almacenamiento local)</td><td>Recordar que ya has visto un aviso de la parroquia para no repetírtelo.</td><td>Hasta que borres los datos del navegador</td></tr>
                    </tbody>
                </table></div>

                <h4>2. De terceros (solo si las aceptas)</h4>
                <p>Algunas páginas muestran contenido de otros servicios. Ese contenido <strong>no se carga hasta que lo aceptas</strong>, y al cargarse el proveedor puede instalar sus propias cookies:</p>
                <div class="table-wrap"><table>
                    <thead><tr><th>Servicio</th><th>Proveedor</th><th>Dónde se usa</th><th>Finalidad</th></tr></thead>
                    <tbody>
                        <tr><td>Google Maps</td><td>Google Ireland Ltd.</td><td>Inicio, Contacto</td><td>Mapa. <a href="https://policies.google.com/technologies/cookies?hl=es" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>YouTube (modo de privacidad mejorada)</td><td>Google Ireland Ltd.</td><td>Imágenes y vídeos</td><td>Reproducir vídeos. <a href="https://policies.google.com/privacy?hl=es" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>SoundCloud</td><td>SoundCloud Global Ltd.</td><td>Homilías</td><td>Reproducir audios. <a href="https://soundcloud.com/pages/cookies" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>Cincopa</td><td>Cincopa Ltd.</td><td>Historia, Eucaristías, Imágenes</td><td>Galerías de fotos.</td></tr>
                        <tr><td>Evangeli.net</td><td>Evangeli.net</td><td>Inicio</td><td>Mostrar el Evangelio del día.</td></tr>
                        <tr><td>Imágenes de noticias</td><td>Vatican News (Santa Sede) / Arzobispado de Barcelona</td><td>Noticias</td><td>Mostrar las fotos de las noticias.</td></tr>
                    </tbody>
                </table></div>

                <h3>Cómo aceptar, rechazar o cambiar tu elección</h3>
                <p>Al entrar por primera vez te mostramos un aviso donde puedes <strong>aceptar</strong>, <strong>rechazar</strong> o <strong>configurar</strong> las cookies de terceros. Puedes cambiar tu decisión en cualquier momento:</p>
                <p><button type="button" class="btn" data-cookie-settings>Configurar cookies</button></p>
                <p>También puedes borrar o bloquear las cookies desde la configuración de tu navegador:
                    <a href="https://support.google.com/chrome/answer/95647?hl=es" target="_blank" rel="noopener">Chrome</a>,
                    <a href="https://support.mozilla.org/es/kb/Borrar%20cookies" target="_blank" rel="noopener">Firefox</a>,
                    <a href="https://support.microsoft.com/es-es/microsoft-edge/eliminar-las-cookies-en-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09" target="_blank" rel="noopener">Edge</a>,
                    <a href="https://support.apple.com/es-es/guide/safari/sfri11471/mac" target="_blank" rel="noopener">Safari</a>.</p>

                <h3>Transferencias internacionales</h3>
                <p>Algunos proveedores están en Estados Unidos. Las transferencias se amparan en el Marco de Privacidad de Datos UE-EE. UU. cuando el proveedor está adherido o, en su defecto, en las cláusulas contractuales tipo de la Comisión Europea. Más información en nuestra <a href="privacidad.html">Política de privacidad</a>.</p>
            </article>
        </section>
""")

# ---------------------------------------------------------------- AVISO LEGAL
PAGES["html/aviso-legal.html"] = page(1, "Aviso legal", "Aviso legal e información del titular de la web de la Parroquia Santa Teresa de Jesús.", cta=False, body=page_hero("Información legal", "Aviso Legal") + """
        <section>
            <article class="prose legal">
                <p class="updated">Última actualización: """ + LEGAL["actualizado"] + """</p>

                <h3>1. Datos del titular</h3>
                <p>En cumplimiento del artículo 10 de la Ley 34/2002, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa:</p>
                <ul class="info-list">
                    <li><strong>Titular</strong>""" + LEGAL["titular"] + """</li>
                    <li><strong>Domicilio</strong>""" + LEGAL["domicilio"] + """</li>
                    <li><strong>Correo electrónico</strong><a href="mailto:""" + LEGAL["email"] + """">""" + LEGAL["email"] + """</a></li>
                </ul>

                <h3>2. Objeto</h3>
                <p>Esta web informa sobre la vida de la parroquia: horarios de celebraciones, actividades pastorales, sacramentos, catequesis y vías de contacto. El acceso es libre y gratuito y no exige registro.</p>

                <h3>3. Uso de la web</h3>
                <p>Quien visita la web se compromete a hacer un uso adecuado de sus contenidos, de acuerdo con la ley, la buena fe y el orden público, y a no emplearlos para actividades ilícitas o que dañen los derechos de la parroquia o de terceros.</p>

                <h3>4. Propiedad intelectual e imágenes</h3>
                <p>Los textos, fotografías y diseño de esta web pertenecen a la parroquia o se usan con autorización de sus autores. No se permite su reproducción con fines comerciales sin permiso. Las fuentes tipográficas utilizadas (Cormorant Garamond y Montserrat) tienen licencia SIL Open Font License.</p>
                <p>Si aparece en alguna fotografía y desea que se retire, puede pedirlo escribiendo a <a href="mailto:""" + LEGAL["email"] + """">""" + LEGAL["email"] + """</a> y lo haremos a la mayor brevedad.</p>

                <h3>5. Enlaces a otras webs</h3>
                <p>La web incluye enlaces a sitios de terceros (Arzobispado de Barcelona, Cáritas, redes sociales, etc.). La parroquia no se responsabiliza de sus contenidos ni de sus políticas de privacidad.</p>

                <h3>6. Responsabilidad</h3>
                <p>La parroquia procura que la información publicada sea correcta y esté actualizada, pero no garantiza la ausencia de errores ni la disponibilidad continua de la web. Los horarios pueden variar en fechas señaladas; ante cualquier duda, consulte con la parroquia.</p>

                <h3>7. Protección de datos y cookies</h3>
                <p>El tratamiento de datos personales se explica en la <a href="privacidad.html">Política de privacidad</a> y el uso de cookies en la <a href="cookies.html">Política de cookies</a>.</p>

                <h3>8. Legislación aplicable</h3>
                <p>Este aviso legal se rige por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales de Barcelona, salvo que la ley disponga otra cosa.</p>
            </article>
        </section>
""")

# ---------------------------------------------------------------- PRIVACIDAD
PAGES["html/privacidad.html"] = page(1, "Política de privacidad", "Cómo trata la Parroquia Santa Teresa de Jesús los datos personales recibidos a través de su web.", cta=False, body=page_hero("Información legal", "Política de Privacidad", crumb="Privacidad") + """
        <section>
            <article class="prose legal">
                <p class="updated">Última actualización: """ + LEGAL["actualizado"] + """</p>

                <p>Esta política explica cómo tratamos los datos personales que nos facilitas a través de esta web, conforme al Reglamento (UE) 2016/679 (RGPD), la Ley Orgánica 3/2018 (LOPDGDD) y el Decreto General de la Conferencia Episcopal Española sobre protección de datos personales.</p>

                <h3>1. Responsable del tratamiento</h3>
                <ul class="info-list">
                    <li><strong>Responsable</strong>""" + LEGAL["titular"] + """</li>
                    <li><strong>Domicilio</strong>""" + LEGAL["domicilio"] + """</li>
                    <li><strong>Correo electrónico</strong><a href="mailto:""" + LEGAL["email"] + """">""" + LEGAL["email"] + """</a></li>
                    <li><strong>Delegado de Protección de Datos</strong>""" + LEGAL["dpd"] + """</li>
                </ul>

                <h3>2. Qué datos tratamos, para qué y con qué base legal</h3>
                <div class="table-wrap"><table>
                    <thead><tr><th>Origen</th><th>Datos</th><th>Finalidad</th><th>Base legal</th></tr></thead>
                    <tbody>
                        <tr><td>Formulario de contacto y correo electrónico</td><td>Nombre, correo y lo que nos escribas</td><td>Responder a tu consulta</td><td>Tu consentimiento (art. 6.1.a RGPD)</td></tr>
                        <tr><td>Formulario de inscripción a la Primera Comunión</td><td>Datos del menor y de su padre, madre o tutor</td><td>Gestionar la inscripción y la catequesis</td><td>Consentimiento del padre, madre o tutor (art. 6.1.a RGPD y art. 7 LOPDGDD) y actividad legítima de una entidad religiosa con sus fieles (art. 9.2.d RGPD)</td></tr>
                        <tr><td>Fotografías de actividades</td><td>Imagen de las personas que aparecen</td><td>Dar a conocer la vida de la parroquia</td><td>Consentimiento de los interesados o de sus representantes legales</td></tr>
                    </tbody>
                </table></div>
                <p>Los datos de <strong>menores de 14 años</strong> solo pueden facilitarlos sus padres o tutores legales.</p>

                <h3>3. Cuánto tiempo los conservamos</h3>
                <p>Los datos de contacto, el tiempo necesario para atender tu consulta. Los de catequesis, mientras dure la formación y, después, durante los plazos que exija la normativa civil o canónica aplicable. En cualquier caso, mientras no solicites su supresión cuando proceda.</p>

                <h3>4. Destinatarios</h3>
                <p>No cedemos datos a terceros salvo obligación legal. Para prestar algunos servicios usamos proveedores que tratan datos por nuestra cuenta (encargados del tratamiento): Google (mapas), FormSubmit (envía por correo a la parroquia los formularios de contacto y de inscripción a la Primera Comunión; no instala cookies) y Netlify (alojamiento de la web). Algunos están en Estados Unidos; las transferencias se amparan en el Marco de Privacidad de Datos UE-EE. UU. cuando el proveedor está adherido o, en su defecto, en las cláusulas contractuales tipo aprobadas por la Comisión Europea.</p>
                <p>Para saber cómo se usa la web, se cuenta de forma anónima qué páginas se visitan (con el idioma, el tipo de pantalla y la web desde la que se llega) y cuántas veces se ven, se empiezan a rellenar y se envían los formularios, con el motivo elegido. No se guardan nombres, correos, mensajes ni direcciones IP, no se usan cookies ni se guarda nada en tu navegador.</p>

                <h3>5. Tus derechos</h3>
                <p>Puedes ejercer en cualquier momento tus derechos de <strong>acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad</strong>, así como <strong>retirar tu consentimiento</strong>, escribiendo a <a href="mailto:""" + LEGAL["email"] + """">""" + LEGAL["email"] + """</a> o por correo postal a la dirección de la parroquia, indicando el derecho que ejerces.</p>
                <p>Si consideras que no hemos atendido correctamente tu solicitud, puedes presentar una reclamación ante la <a href="https://www.aepd.es" target="_blank" rel="noopener">Agencia Española de Protección de Datos</a>.</p>

                <h3>6. Seguridad</h3>
                <p>Aplicamos medidas técnicas y organizativas adecuadas para proteger los datos frente a pérdidas, accesos no autorizados o alteraciones.</p>

                <h3>7. Cookies</h3>
                <p>Consulta nuestra <a href="cookies.html">Política de cookies</a>.</p>
            </article>
        </section>
""")

PAGES["404.html"] = page(0, "Página no encontrada", "La página que buscas no existe en la web de la Parroquia Santa Teresa de Jesús.", body="""        <section class="hero" style="height:auto; min-height:100vh;">
            <div class="hero-bg" aria-hidden="true"></div>
            <span class="eyebrow">Error 404</span>
            <h1>Página no<br>encontrada</h1>
            <div class="hero-divider"></div>
            <p>Lo sentimos, la página que buscas no existe o ha cambiado de sitio.</p>
            <div class="hero-actions">
                <a href="/" class="btn btn-solid">Volver al inicio</a>
                <a href="/html/contacto.html" class="btn btn-light">Contactar</a>
            </div>
        </section>
""")

import re

SERVICES = [
    ("google.com/maps", "Google Maps"),
    ("calendar.google.com", "Google Calendar"),
    ("esglesia.barcelona", "Arzobispado de Barcelona (buscador de parroquias)"),
    ("docs.google.com/forms", "Google Forms (formulario)"),
    ("youtube", "YouTube"),
    ("soundcloud.com", "SoundCloud"),
    ("evangeli.net", "Evangeli.net (Evangelio del día)"),
]


def block_iframes(html):
    """Las iframes de terceros no se cargan hasta que el visitante acepta el contenido externo."""
    def sub(m):
        attrs_a, url, attrs_b = m.group(1), m.group(2), m.group(3)
        service = next((name for key, name in SERVICES if key in url), "contenido externo")
        return (f'<div class="consent-embed" data-service="{service}">'
                f'<iframe{attrs_a} data-consent-src="{url}"{attrs_b}>{m.group(4)}</iframe></div>')
    return re.sub(r'<iframe\b([^>]*?)\ssrc="(https?://[^"]+)"([^>]*)>(.*?)</iframe>', sub, html, flags=re.S)


def block_scripts(html):
    # Instagram (Elfsight)
    html = html.replace('<script src="https://elfsightcdn.com/platform.js" async></script>',
                        '<script type="text/plain" data-consent="embeds" data-src="https://elfsightcdn.com/platform.js"></script>')
    html = re.sub(r'(<div class="elfsight-app-[^"]+"[^>]*></div>)',
                  r'<div class="consent-embed" data-service="Instagram (Elfsight)">\1</div>', html)
    # Typeform
    html = re.sub(r'(<div class="typeform-widget"[^>]*></div>)',
                  r'<div class="consent-embed" data-service="Typeform (formulario)">\1</div>', html)
    html = html.replace('<script> (function() { var qs,js,q,s,d=document',
                        '<script type="text/plain" data-consent="embeds"> (function() { var qs,js,q,s,d=document')
    return html


import importlib.util
import json
import posixpath
from datetime import date

_S = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_S, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


i18n = _load("i18n")
_ALL_TR = dict(_load("translations").TR)
_ALL_TR.update(_load("translations_homilias").TR_HOMILIAS)
TABLE = {es: {"ca": (v[0] if v else es), "en": (v[1] if v else es)} for es, v in _ALL_TR.items()}
# Textos de las reflexiones subidas desde el panel: si no tienen traducción, se muestran tal cual
for _h in HOMILIAS:
    for _k in (_h.get("titulo"), _h.get("kicker"), _h.get("extracto"), _h.get("saludo"), _h.get("autor_nombre"),
               _h.get("autor_cargo"), _first_quote(_h.get("texto"))):
        if _k:
            TABLE.setdefault(_k.strip(), {"ca": _k.strip(), "en": _k.strip()})
for _es, _ca, _en in [("Celebraciones", "Celebracions", "Celebrations"), ("Comunidad", "Comunitat", "Community"),
                      ("Actualidad", "Actualitat", "News"), ("La parroquia", "La parròquia", "The parish"),
                      ("Eucaristía", "Eucaristia", "Eucharist"), ("Calendario semanal", "Calendari setmanal", "Weekly schedule"),
                      ("Matrimonio y aniversarios", "Matrimoni i aniversaris", "Marriage and anniversaries"),
                      ("Palabra de Dios", "Paraula de Déu", "Word of God"), ("Iglesia", "Església", "Church"),
                      ("Vaticano y Arzobispado", "Vaticà i Arquebisbat", "Vatican and Archdiocese"),
                      ("Consejos parroquiales", "Consells parroquials", "Parish councils"), ("Ver todo", "Veure-ho tot", "See all"),
                      ("Inicio", "Inici", "Home"), ("Bienvenidos", "Benvinguts", "Welcome"), ("Quiénes somos", "Qui som", "About us"),
                      ("Próxima misa y horarios", "Propera missa i horaris", "Next Mass and times"),
                      ("Reflexión de la semana", "Reflexió de la setmana", "This week's reflection"),
                      ("Buscar una parroquia", "Cercar una parròquia", "Find a parish"),
                      ("¿Es tu primera visita?", "És la teva primera visita?", "First time here?"),
                      ("Horarios y cómo llegar", "Horaris i com arribar-hi", "Times and how to get here"),
                      ("Adoración al Santísimo", "Adoració al Santíssim", "Eucharistic adoration"),
                      ("Media hora con bendición", "Mitja hora amb benedicció", "Half an hour with benediction"),
                      ("Noticias de la parroquia", "Notícies de la parròquia", "Parish news"),
                      ("Lo que pasa en Santa Teresa", "El que passa a Santa Teresa", "What's happening at Santa Teresa"),
                      ("Muy pronto publicaremos aquí las noticias de la parroquia.", "Ben aviat publicarem aquí les notícies de la parròquia.", "Parish news will be published here very soon."),
                      ("Más en nuestro Instagram", "Més al nostre Instagram", "More on our Instagram"),
                      ("Noticias de la Iglesia", "Notícies de l'Església", "Church news"),
                      ("Todas las noticias de la parroquia", "Totes les notícies de la parròquia", "All parish news"),
                      ("Más noticias de la parroquia", "Més notícies de la parròquia", "More parish news"),
                      ("Últimas noticias", "Darreres notícies", "Latest news"),
                      ("Más información", "Més informació", "More information"),
                      ("Noticias de la parroquia | Parroquia Santa Teresa de Jesús", "Notícies de la parròquia | Parròquia de Santa Teresa de Jesús", "Parish news | Santa Teresa de Jesús Parish"),
                      ("Noticias de la Parroquia Santa Teresa de Jesús, en el barrio del Carmel (Barcelona).", "Notícies de la Parròquia de Santa Teresa de Jesús, al barri del Carmel (Barcelona).", "News from Santa Teresa de Jesús Parish, in the Carmel neighbourhood (Barcelona)."),
                      ("Buscar una parroquia | Parroquia Santa Teresa de Jesús", "Cercar una parròquia | Parròquia de Santa Teresa de Jesús", "Find a parish | Santa Teresa de Jesús Parish"),
                      ("Encuentra cualquier parroquia de la archidiócesis de Barcelona sin salir de la web de la Parroquia Santa Teresa de Jesús.", "Troba qualsevol parròquia de l'arxidiòcesi de Barcelona sense sortir del web de la Parròquia de Santa Teresa de Jesús.", "Find any parish in the Archdiocese of Barcelona without leaving the Santa Teresa de Jesús Parish website."),
                      ("Archidiócesis de Barcelona", "Arxidiòcesi de Barcelona", "Archdiocese of Barcelona"),
                      ("Buscador de parroquias", "Cercador de parròquies", "Parish finder"),
                      ("Todas las parroquias de Barcelona", "Totes les parròquies de Barcelona", "All the parishes of Barcelona"),
                      ("Busca por nombre, barrio o población con el buscador oficial del Arzobispado de Barcelona, aquí mismo.", "Cerca per nom, barri o població amb el cercador oficial de l'Arquebisbat de Barcelona, aquí mateix.", "Search by name, neighbourhood or town with the official Archdiocese of Barcelona finder, right here."),
                      ("Buscador de parroquias del Arzobispado de Barcelona", "Cercador de parròquies de l'Arquebisbat de Barcelona", "Archdiocese of Barcelona parish finder"),
                      ("Arzobispado de Barcelona (buscador de parroquias)", "Arquebisbat de Barcelona (cercador de parròquies)", "Archdiocese of Barcelona (parish finder)"),
                      ("Carrer del Llobregós, 132 · 08032 Barcelona · El Carmel", "Carrer del Llobregós, 132 · 08032 Barcelona · El Carmel", "Carrer del Llobregós, 132 · 08032 Barcelona · El Carmel"),
                      ("¿Quieres colaborar?", "Vols col·laborar?", "Would you like to help?"),
                      ("Únete a un grupo de la parroquia", "Uneix-te a un grup de la parròquia", "Join a parish group"),
                      ("Información e inscripción &rarr;", "Informació i inscripció &rarr;", "Information and registration &rarr;"),
                      ("Parroquia", "Parròquia", "Parish"), ("Vida de la comunidad", "Vida de la comunitat", "Community life"),
                      ("Organización", "Organització", "Organisation"), ("Estamos para ayudarte", "Som aquí per ajudar-te", "We are here to help"),
                      ("¿Quieres pedir un sacramento?", "Vols demanar un sagrament?", "Would you like to request a sacrament?"),
                      ("Escríbenos y te acompañamos", "Escriu-nos i t'acompanyem", "Write to us and we will help you"),
                      ("¿Guardas fotos antiguas?", "Guardes fotos antigues?", "Do you have old photos?"),
                      ("Compártelas con el archivo", "Comparteix-les amb l'arxiu", "Share them with the archive"), ("Contacto", "Contacte", "Contact")]:
    TABLE[_es] = {"ca": _ca, "en": _en}
for _k, _l, _p, _c in NAV:
    _tl = TABLE.get(_l, {"ca": _l, "en": _l})
    TABLE[f"{_l}: submenú"] = {"ca": f"{_tl['ca']}: submenú", "en": f"{_tl['en']}: submenu"}
for _es, _ca, _en in SAC_TR:
    TABLE[_es] = {"ca": _ca, "en": _en}
# Revista digital: los textos escritos en el panel con sus traducciones opcionales (sin traducción, tal cual)
_rt = REVISTA.get("traducciones") or {}
def _rev_pair(es_txt, ca_txt, en_txt):
    es_txt = esc(es_txt).strip()
    if es_txt:
        TABLE[es_txt] = {"ca": esc(ca_txt).strip() or es_txt, "en": esc(en_txt).strip() or es_txt}
_rev_pair(REVISTA.get("titulo"), _rt.get("titulo_ca"), _rt.get("titulo_en"))
_rev_es, _rev_ca, _rev_en = _paragraphs(REVISTA.get("texto")), _paragraphs(_rt.get("texto_ca")), _paragraphs(_rt.get("texto_en"))
for _i, _p in enumerate(_rev_es):
    # cada párrafo con el suyo; si el número de párrafos no coincide, ese idioma se queda en castellano
    _rev_pair(_p, _rev_ca[_i] if len(_rev_ca) == len(_rev_es) else "", _rev_en[_i] if len(_rev_en) == len(_rev_es) else "")
if REVISTA.get("numero"):
    TABLE.setdefault(esc(REVISTA["numero"]).strip(), {"ca": esc(REVISTA["numero"]).strip(), "en": esc(REVISTA["numero"]).strip()})
# Números y artículos: títulos, firmas, entradillas, pies de foto y presentaciones se muestran tal cual.
# El cuerpo de cada artículo no: así, en catalán e inglés sale el aviso «texto original en castellano».
_rev_frag = []
for _n in REV_ISSUES:
    _rev_frag += [_n["titulo"], _n["extracto"], f"{rev_label(_n)} · {_n['titulo']}" if _n.get("num") else ""]
    _rev_frag += [HOM.markdown(_n.get("presentacion", ""))]
    for _a in _n["articulos"]:
        _rev_frag += [_a["titulo"], _a.get("autor"), _a.get("seccion"), _a.get("pie"), _a.get("entradilla"), _a["extracto"]]
def _rev_tr(es_txt, ca_txt, en_txt):
    TABLE[es_txt.strip()] = {"ca": ca_txt.strip(), "en": en_txt.strip()}
_SUF = ("| Parroquia Santa Teresa de Jesús", "| Parròquia de Santa Teresa de Jesús", "| Santa Teresa de Jesús Parish")
_DESC = ("revista digital de la Parroquia Santa Teresa de Jesús.", "revista digital de la Parròquia de Santa Teresa de Jesús.", "digital magazine of Santa Teresa de Jesús Parish.")
for _n in REV_ISSUES:
    _t = qesc(_n["titulo"])
    _rev_tr(f"{_t} · Revista digital {_SUF[0]}", f"{_t} · Revista digital {_SUF[1]}", f"{_t} · Digital magazine {_SUF[2]}")
    _rev_tr(f"{_t} — {_DESC[0]}", f"{_t} — {_DESC[1]}", f"{_t} — {_DESC[2]}")
    if _n.get("num"):
        _k, _te = _n["num"], esc(_n["titulo"])
        _rev_tr(f"Número {_k}", f"Número {_k}", f"Issue {_k}")
        _rev_tr(f"Revista digital · Número {_k}", f"Revista digital · Número {_k}", f"Digital magazine · Issue {_k}")
        _rev_tr(f"Número {_k} · {_te}", f"Número {_k} · {_te}", f"Issue {_k} · {_te}")
    for _a in _n["articulos"]:
        _at = qesc(_a["titulo"])
        _rev_tr(f"{_at} {_SUF[0]}", f"{_at} {_SUF[1]}", f"{_at} {_SUF[2]}")
        _rev_tr(f"{_at} — {_DESC[0]}", f"{_at} — {_DESC[1]}", f"{_at} — {_DESC[2]}")
        if _a["extracto"]:
            TABLE.setdefault(qesc(_a["extracto"][:180]).strip(), {"ca": qesc(_a["extracto"][:180]).strip(), "en": qesc(_a["extracto"][:180]).strip()})
for _n in NEWS:
    _rev_frag += [_n["titulo"], _n["extracto"], _n.get("pie"), _n.get("resumen")]
    _t = qesc(_n["titulo"])
    _rev_tr(f"{_t} {_SUF[0]}", f"{_t} {_SUF[1]}", f"{_t} {_SUF[2]}")
    _d = qesc((_n["extracto"] or _n["titulo"])[:180]).strip()
    TABLE.setdefault(_d, {"ca": _d, "en": _d})
for _frag in _rev_frag:
    if not _frag:
        continue
    _html_frag = _frag if "<" in _frag else f"<p>{esc(_frag)}</p>"
    for _k in i18n.extract(_html_frag, "html/revista.html") + ([esc(_frag).strip()] if "<" not in _frag else []):
        TABLE.setdefault(_k.strip(), {"ca": _k.strip(), "en": _k.strip()})
# El texto de la última reflexión aparece entero en la portada: sin traducción, se queda tal cual
if HOMILIAS:
    for _k in i18n.extract(HOM.markdown(HOM.home_text(HOMILIAS[0].get("texto", ""))[0]), "index.html") + [notice_text(HOMILIAS[0])]:
        TABLE.setdefault(_k.strip(), {"ca": _k.strip(), "en": _k.strip()})
LANGS = ["es", "ca", "en"]
LOCALES = {"es": "es_ES", "ca": "ca_ES", "en": "en_GB"}
LANG_NAMES = [("es", "ES", "Español"), ("ca", "CA", "Català"), ("en", "EN", "English")]
HOMILY_NOTE = {"ca": "Text original en castellà.", "en": "Original text in Spanish."}
REVISTA_NOTE = {"ca": "Article original en castellà.", "en": "Original article in Spanish."}
NEWS_NOTE = {"ca": "Notícia original en castellà.", "en": "Original news item in Spanish."}


def out_path(lang, rel):
    return rel if lang == "es" else f"{lang}/{rel}"


def page_url(lang, rel):
    """Dirección pública de la página (tildes y eñes codificadas, como piden Google y los sitemaps)."""
    from urllib.parse import quote
    p = out_path(lang, rel)
    if p.endswith("index.html"):
        p = p[:-len("index.html")]
    elif p.endswith(".html"):
        p = p[:-len(".html")]
    return SITE + quote(p)


def relurl(from_path, to_path):
    return posixpath.relpath(to_path, posixpath.dirname(from_path) or ".")


def lang_switch(lang, rel):
    cur = out_path(lang, rel)
    links = "".join(
        f'<a href="{relurl(cur, out_path(l, rel))}" hreflang="{l}" lang="{l}" title="{name}"'
        f'{" aria-current=\"true\"" if l == lang else ""}>{label}</a>'
        for l, label, name in LANG_NAMES)
    return f'        <div class="lang-switch" role="navigation" aria-label="Idioma / Language">{links}</div>\n'


MENU_TEXT = {
    "es": ("Horarios de misa", "Laborables y sábados · 19:00 h", "Domingos · 11:00 y 13:15 h", "Idioma"),
    "ca": ("Horaris de missa", "Feiners i dissabtes · 19:00 h", "Diumenges · 11:00 i 13:15 h", "Idioma"),
    "en": ("Mass times", "Weekdays and Saturdays · 19:00", "Sundays · 11:00 and 13:15", "Language"),
}


def menu_extra(lang, rel, with_lang=True):
    """Bloque que solo se ve en el menú del móvil: horarios de misa y selector de idioma grande."""
    title, weekdays, sundays, lang_label = MENU_TEXT[lang]
    langs = ""
    if with_lang:
        cur = out_path(lang, rel)
        links = "".join(
            f'<a href="{relurl(cur, out_path(l, rel))}" hreflang="{l}" lang="{l}"'
            f'{" aria-current=\"true\"" if l == lang else ""}>{name}</a>'
            for l, label, name in LANG_NAMES)
        langs = f'<div class="nav-lang" role="group" aria-label="{lang_label}">{links}</div>'
    return (f'            <li class="nav-extra">\n'
            f'                <div class="nav-mass"><span class="nav-mass-title">{title}</span>'
            f'<span>{weekdays}</span><span>{sundays}</span></div>\n'
            f'                {langs}\n            </li>\n')


def hreflang_links(rel):
    out = "".join(f'    <link rel="alternate" hreflang="{l}" href="{page_url(l, rel)}">\n' for l in LANGS)
    return out + f'    <link rel="alternate" hreflang="x-default" href="{page_url("es", rel)}">\n'


def jsonld(obj):
    return '    <script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


def structured_data(html, lang, rel):
    extra = ""
    if rel == "index.html":
        extra += jsonld({"@context": "https://schema.org", "@type": "WebSite", "name": "Parroquia Santa Teresa de Jesús",
                         "alternateName": ["Parròquia de Santa Teresa de Jesús", "Parroquia Santa Teresa de Jesús Barcelona"],
                         "url": page_url(lang, rel), "inLanguage": lang,
                         "publisher": {"@id": "https://parroquiasantateresabcn.netlify.app/#parroquia"}})
    else:
        m = re.search(r'<nav class="breadcrumb"[^>]*><a [^>]*>(.*?)</a><span>/</span>(.*?)</nav>', html)
        if m:
            extra += jsonld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": m.group(1), "item": page_url(lang, "index.html")},
                {"@type": "ListItem", "position": 2, "name": m.group(2), "item": page_url(lang, rel)}]})
    return html.replace("</head>", extra + "</head>", 1)


def relocate_assets(html):
    """Las páginas de /ca y /en están una carpeta más abajo: los recursos comunes suben un nivel."""
    html = re.sub(r'((?:href|src|data-src|data-bg)=")((?:\.\./)*)(css/|js/|fotosdefinitivas/|fonts/|data/|favicon|apple-touch-icon|site\.webmanifest)',
                  r'\1../\2\3', html)
    return re.sub(r"url\('((?:\.\./)*)fotosdefinitivas/", r"url('../\1fotosdefinitivas/", html)


missing = set()
written = []
for rel, base in PAGES.items():
    base = block_scripts(block_iframes(base))
    if rel == "404.html":
        # la 404 se sirve desde cualquier ruta: rutas absolutas desde la raíz, y fuera del índice de Google
        html = base.replace('    <link rel="canonical" href="__URL__">\n__HREFLANG__', '    <meta name="robots" content="noindex">\n')
        html = html.replace("__URL__", SITE).replace("__LOCALE__", "es_ES")
        html = re.sub(r'(href|src)="(?!https?:|//|mailto:|/|#contenido")([^"]*)"', r'\1="/\2"', html)
        html = html.replace("__LANGSWITCH__", "").replace("__MENU_EXTRA__", menu_extra("es", rel, with_lang=False))
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        continue

    for lang in LANGS:
        html = base
        if lang != "es":
            if rel.startswith(("html/reflexiones/", "html/noticias/")) or "--" in rel and rel.startswith("html/revista/"):
                # reflexión subida desde el panel: si su texto aún no está traducido, se muestra
                # en castellano con un aviso (sin contarla como texto pendiente del generador)
                _art = re.search(r'<article class="prose.*?</article>', html, re.S)
                _pend = _art and any(k not in TABLE for k in i18n.extract(_art.group(0), rel))
                html = i18n.translate(html, rel, lang, TABLE, set())
                if _pend:
                    _note = (REVISTA_NOTE if rel.startswith("html/revista/") else NEWS_NOTE if rel.startswith("html/noticias/") else HOMILY_NOTE)[lang]
                    html = html.replace('<article class="prose', f'<p class="lang-note">{_note}</p>\n                <article class="prose', 1)
            else:
                html = i18n.translate(html, rel, lang, TABLE, missing)
            html = html.replace('<html lang="es">', f'<html lang="{lang}">', 1)
            html = relocate_assets(html)
            # Evangelio para la familia: la versión de evangeli.net en el idioma de la página
            html = html.replace(FAMILY_URL, FAMILY_URL[:-2] + lang)
        html = (html.replace("__URL__", page_url(lang, rel))
                    .replace("__HREFLANG__", hreflang_links(rel))
                    .replace("__LOCALE__", LOCALES[lang])
                    .replace("__LANGSWITCH__", lang_switch(lang, rel))
                    .replace("__MENU_EXTRA__", menu_extra(lang, rel)))
        html = structured_data(html, lang, rel)
        path = os.path.join(ROOT, out_path(lang, rel))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        written.append((lang, rel))

# ---------- borrar las páginas de reflexiones, números o artículos que ya no están publicados ----------
# (las carpetas html/reflexiones y html/revista solo contienen páginas generadas desde el panel)
_keep = {out_path(l, r) for l, r in written}
for _sub in ("html/reflexiones", "html/revista", "html/noticias"):
    for _lang in LANGS:
        _dir = os.path.join(ROOT, out_path(_lang, _sub))
        if os.path.isdir(_dir):
            for _f in os.listdir(_dir):
                _rel = out_path(_lang, _sub + "/" + _f)
                if _f.endswith(".html") and _rel not in _keep:
                    os.remove(os.path.join(_dir, _f))
                    print("Página retirada (ya no está publicada):", _rel)

# ---------- sitemap.xml y robots.txt ----------
today = date.today().isoformat()
urls = []
for rel in [r for r in PAGES if r != "404.html"]:
    alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l, rel)}"/>' for l in LANGS)
    alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{page_url("es", rel)}"/>'
    prio = "1.0" if rel == "index.html" else ("0.3" if rel in ("html/aviso-legal.html", "html/privacidad.html", "html/cookies.html") else "0.7")
    for lang in LANGS:
        urls.append(f"  <url>\n    <loc>{page_url(lang, rel)}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{prio}</priority>{alts}\n  </url>")
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(f"User-agent: *\nAllow: /\nDisallow: /scripts/\nDisallow: /admin/\nDisallow: /contenido/\n\nSitemap: {SITE}sitemap.xml\n")

print(len(written), "páginas escritas en", len(LANGS), "idiomas;", len(urls), "URL en sitemap.xml")
if missing:
    print("SIN TRADUCIR:", len(missing))
    for m_ in sorted(missing):
        print("  -", m_[:110].encode("ascii", "replace").decode())
