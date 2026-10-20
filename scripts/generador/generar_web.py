import sys, os, re

ROOT = sys.argv[1]

import html as _html
import importlib.util as _ilu
_hs = _ilu.spec_from_file_location("homilias", os.path.join(os.path.dirname(os.path.abspath(__file__)), "homilias.py"))
HOM = _ilu.module_from_spec(_hs); _hs.loader.exec_module(HOM)
HOMILIAS, AUTORES = HOM.load(ROOT)
esc = lambda t: _html.escape(t or "", quote=False)

# Versión de cada archivo común (huella de su contenido): al cambiar el archivo cambia su
# dirección (site.css?v=...) y ningún navegador puede seguir usando una copia antigua.
import hashlib as _hashlib
V = {}
for _f in ("css/fonts.css", "css/site.css", "js/site.js", "data/avisos.js"):
    with open(os.path.join(ROOT, _f), "rb") as _fh:
        V[_f] = _hashlib.md5(_fh.read()).hexdigest()[:10]

NAV = [
    ("inicio", "Inicio", "index.html", [
        ("Horarios de misa", "index.html#horarios"),
        ("Bienvenidos", "index.html#bienvenida"),
        ("Reflexión dominical", "index.html#reflexion"),
        ("Vida parroquial", "index.html#vida"),
        ("Sacramentos", "index.html#sacramentos"),
        ("La parroquia en imágenes", "index.html#galeria"),
        ("Evangelio de hoy", "index.html#actualidad"),
    ]),
    ("eucaristias", "Eucaristías", "html/misas.html", [
        ("Horarios de Eucaristía", "html/misas.html#horarios"),
        ("Misa con coro góspel", "html/misas.html#gospel"),
        ("Calendario de eucaristías y actividades", "html/misas.html#calendario"),
        ("Sacramentos", "html/adminsacra.html"),
        ("Catequesis", "html/catequesis.html"),
    ]),
    ("noticias", "Noticias", "html/noticias.html", [
        ("§", "Actualidad de la Iglesia"),
        ("Vaticano y Arzobispado de Barcelona", "html/noticias.html"),
        ("§parish", "De nuestra parroquia"),
        ("+Última reflexión", "__ULTIMA__"),
        ("+Todas las reflexiones", "html/humiliasmenu.html"),
    ]),
    ("dinamica", "Dinámica Pastoral", "html/dinamicapastoral.html", [
        ("Grupos y servicios", "html/dinamicapastoral.html"),
        ("Catequesis", "html/catequesis.html"),
        ("Jóvenes", "html/jovenes2alternativa.html"),
        ("Sacramentos", "html/adminsacra.html"),
        ("Imágenes y vídeos", "html/imagenes.html"),
    ]),
    ("organigrama", "Organigrama", "html/organigramaparroquial.html", [
        ("Nuestra estructura", "html/organigramaparroquial.html#estructura"),
        ("Consejo parroquial", "html/organigramaparroquial.html#consejos"),
        ("Consejo económico", "html/organigramaparroquial.html#consejos"),
    ]),
    ("historia", "Historia", "html/historia.html", [
        ("Nuestra historia", "html/historia.html#parroquia"),
        ("Línea del tiempo", "html/historia.html#linea-del-tiempo"),
        ("Archivo histórico", "html/historia.html#archivo"),
        ("Imágenes y vídeos", "html/imagenes.html"),
    ]),
    ("contacto", "Contacto", "html/contacto.html", [
        ("Dirección y horarios", "html/contacto.html#datos"),
        ("Contacta con nosotros", "html/contacto.html#escribenos"),
        ("Despacho parroquial", "html/adminsacra.html#despacho"),
        ("Política de privacidad", "html/privacidad.html"),
    ]),
]

if HOMILIAS:
    NAV = [(k, l, p, [(a, HOMILIAS[0]["url"] if b == "__ULTIMA__" else b) for a, b in ch]) for k, l, p, ch in NAV]
else:
    NAV = [(k, l, p, [(a, b) for a, b in ch if b != "__ULTIMA__"]) for k, l, p, ch in NAV]

CHEVRON = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>')


PARISH_ICON = ('<svg class="parish-ico" viewBox="0 0 26 34" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round">'
               '<path d="M13 1.5v31M4.5 10.5h17" stroke-width="2.4"/><circle cx="13" cy="10.5" r="3.4" stroke-width="1.6"/></svg>')


def nav_items(depth, active):
    out = []
    for key, label, path, children in NAV:
        cur = key == active
        rows = []
        for l, p in children:
            if l.startswith("§"):   # encabezado de grupo dentro del submenú
                cls = "sub-heading" + (" parish" if l == "§parish" else "")
                rows.append(f'                    <li class="{cls}" aria-hidden="true">{p}</li>')
            elif l.startswith("+"):  # contenido propio de la parroquia: estilo diferenciado
                rows.append(f'                    <li class="parish-item"><a href="{href(p, depth)}" class="sub-link parish-link">{PARISH_ICON}<span>{l[1:]}</span></a></li>')
            else:
                rows.append(f'                    <li><a href="{href(p, depth)}" class="sub-link">{l}</a></li>')
        subs = "\n".join(rows)
        out.append(
            f'            <li class="nav-item has-sub">\n'
            f'                <a href="{href(path, depth)}" class="nav-link{" active" if cur else ""}"{" aria-current=\"page\"" if cur else ""}>{label}</a>\n'
            f'                <button type="button" class="sub-toggle" aria-expanded="false" aria-label="Submenú">{CHEVRON}</button>\n'
            f'                <ul class="sub-menu">\n{subs}\n                </ul>\n'
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

# Datos del titular para Aviso legal y Privacidad.
# Los marcados como PENDIENTE deben completarse con los datos reales de la parroquia.
LEGAL = {
    "titular": "Parroquia de Santa Teresa de Jesús (Arzobispado de Barcelona)",
    "domicilio": "Carrer del Llobregós, 132, 08032 Barcelona",
    "email": "parroquisantateresabarcelona@gmail.com",
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
    <link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
    <link rel="icon" href="{p}favicon-48.png" sizes="48x48" type="image/png">
    <link rel="apple-touch-icon" href="{p}apple-touch-icon.png">
    <link rel="manifest" href="{p}site.webmanifest">

    <link rel="stylesheet" href="{p}css/fonts.css?v={V["css/fonts.css"]}">
    <link rel="stylesheet" href="{p}css/site.css?v={V["css/site.css"]}">
    <meta name="theme-color" content="#bfa065">
    <script>document.documentElement.classList.add("js");</script>
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
                    <li><a href="https://www.esglesiabarcelona.cat/mapa/index.php?view=barcelona-santateresadejesus" target="_blank" rel="noopener">Buscador de Parroquias</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Contacto</h4>
                <ul class="footer-links">
                    <li><a href="{href('html/contacto.html', depth)}">Contactar</a></li>
                    <li><a href="https://www.instagram.com/parroquiasantateresadejesusbcn/" target="_blank" rel="noopener">Instagram</a></li>
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
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="1.5"/><path d="M3.5 6.5l8.5 7 8.5-7"/></svg>',
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


def icon_card(icon, title, text, link):
    return f"""                <a class="icon-card" href="{link}">
                    <div class="icon-circle">{SAC_ICONS[icon]}</div>
                    <h3>{title}</h3>
                    <p>{text}</p>
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
    ("dsc_0565.jpg", "Vidriera de Santa Teresa con el Niño Jesús", ""),
    ("dsc_0589.jpg", "Bendición de ramos en el Domingo de Ramos", ""),
    ("dsc_0599webog.jpg", "El campanario durante el Domingo de Ramos", "tall"),
    ("img_5434.jpg", "Celebración de la eucaristía", ""),
    ("dsc_0574.jpg", "Imágenes del presbiterio", ""),
    ("dsc_0512.jpg", "La comunidad reunida en la iglesia", "wide"),
]

INDEX_HEAD = """    <link rel="preload" as="image" href="fotosdefinitivas/web/portada3.jpg">
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
      "email": "parroquisantateresabarcelona@gmail.com",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Carrer del Llobregós, 132",
        "postalCode": "08032",
        "addressLocality": "Barcelona",
        "addressCountry": "ES"
      },
      "sameAs": ["https://www.instagram.com/parroquiasantateresadejesusbcn/"]
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


def home_homily():
    if not HOMILIAS:
        return ""
    h = HOMILIAS[0]
    quote = _first_quote(h.get("texto"))
    quote_html = (f'<blockquote class="book-quote"><span aria-hidden="true">&ldquo;</span>{esc(quote)}</blockquote>' if quote else "")
    others = "".join(
        f"""
                <a class="homily-chip" href="{o["url"]}">
                    {_portrait(o, 0, "chip-photo")}
                    <span><strong>{esc(o["titulo"])}</strong><em><span>{esc(o["autor_nombre"])}</span> · {date_long(o)}</em></span>
                </a>""" for o in HOMILIAS[1:3])
    return f"""        <section id="reflexion" class="homily">
            <div class="section-head">
                <span class="subtitulo">De nuestra parroquia</span>
                <h2>Reflexión dominical</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="open-book">
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
                        <span class="book-kicker">{esc(h["kicker"]) or date_long(h)}</span>
                        <h3>{esc(h["titulo"])}</h3>
                        <p class="illuminated">{esc(h["extracto"])}</p>
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
full_title="Parroquia Santa Teresa de Jesús | Barcelona", active="inicio", extra_head=INDEX_HEAD, body="""        <section class="hero">
            <div class="hero-bg" aria-hidden="true"></div>
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
                    <div class="time">11:00 <small>·</small> 13:00</div>
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

        <section class="image-band" style="background-image:url('fotosdefinitivas/web/portada2.jpg')">
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
            <div class="icon-grid">
""" + "\n".join([
    icon_card("agua", "Bautismo", "Ceremonias bautismales al mediodía en cualquier domingo del año que se pida.", "html/adminsacra.html"),
    icon_card("paloma", "Confirmación", "Se celebra cada tres años, con catequesis a partir de los 14 años.", "html/catequesis.html"),
    icon_card("anillos", "Matrimonio", "Bodas y preparación: consulta en el despacho parroquial los viernes por la tarde.", "html/contacto.html"),
    icon_card("manos", "Perdón", "Los sábados de 18:30 a 19:00 h y siempre un rato antes de cada misa.", "html/adminsacra.html"),
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
                <hr class="section-divider" style="margin-bottom:1.5rem;">
                <a href="html/noticias.html" class="link-arrow">Noticias del Vaticano y del Arzobispado <span>&rarr;</span></a>
            </div>

            <div class="grid-container">
                <div class="widget-container">
                    <h3>Evangelio de Hoy</h3>
                    <div class="gospel-frame">
                        <iframe title="Evangelio de hoy" width="100%" height="680" frameborder="0" loading="lazy" src="https://evangeli.net/evangelio/widget/web"></iframe>
                    </div>
                    <a href="https://evangeli.net/evangelio" class="btn gospel-more" target="_blank" rel="noopener">Leer el Evangelio completo &rarr;</a>
                </div>

                <div class="widget-container">
                    <h3>@parroquiasantateresadejesusbcn</h3>
                    <script src="https://elfsightcdn.com/platform.js" async></script>
                    <div class="elfsight-app-8b9a40bb-7d76-4b43-bf12-9ed787fa24e2" data-elfsight-app-lazy></div>
                </div>
            </div>
        </section>

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
                        <li><strong>Correo electrónico</strong><a href="mailto:parroquisantateresabarcelona@gmail.com">parroquisantateresabarcelona@gmail.com</a></li>
                    </ul>
                    <div class="btn-group">
                        <a href="html/contacto.html" class="btn btn-solid">Contactar</a>
                        <a href="https://goo.gl/maps/Y4SiUkiMGwp" class="btn btn-light" target="_blank" rel="noopener">Cómo llegar</a>
                    </div>
                </div>
            </div>
        </section>
""")

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
     ("contacto.html", "Solicitar visita", False)),
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
                <a href="contacto.html" class="btn">Compartir fotos</a>
            </div>
        </section>
""")

# ---------------------------------------------------------------- CONTACTO
PAGES["html/contacto.html"] = page(1, "Contacto", "Contacta con la Parroquia Santa Teresa de Jesús: Carrer del Llobregós, 132, 08032 Barcelona.", active="contacto", body=page_hero("Estamos para ayudarte", "Contacto", "web/portada1.jpg") + """
        <section class="schedule-section" id="datos">
            <div class="info-cards">
""" + "\n".join([
    info_card("pin", "Dirección", 'Carrer del Llobregós, 132<br>08032 Barcelona<br><a href="https://goo.gl/maps/Y4SiUkiMGwp" target="_blank" rel="noopener">Cómo llegar &rarr;</a>'),
    info_card("mail", "Correo electrónico", '<a href="mailto:parroquisantateresabarcelona@gmail.com">parroquisantateresabarcelona<wbr>@gmail.com</a>'),
    info_card("reloj", "Despacho parroquial", "Viernes por la tarde, y un rato antes o después de cada misa"),
    info_card("insta", "Instagram", '<a href="https://www.instagram.com/parroquiasantateresadejesusbcn/" target="_blank" rel="noopener">@parroquiasantateresadejesusbcn</a>'),
]) + """
            </div>
        </section>

        <section style="padding-top:2rem;" id="escribenos">
            <div class="two-col">
                <div>
                    <span class="subtitulo text-left">Escríbenos</span>
                    <h2 class="text-left">Contacta con nosotros</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <div class="embed-frame" style="padding:0.5rem;">
                        <div class="typeform-widget" data-url="https://parroquisantateresabarcelona.typeform.com/to/kceJJ6" style="width: 100%; height: 520px;"></div>
                    </div>
                    <script> (function() { var qs,js,q,s,d=document, gi=d.getElementById, ce=d.createElement, gt=d.getElementsByTagName, id="typef_orm", b="https://embed.typeform.com/"; if(!gi.call(d,id)) { js=ce.call(d,"script"); js.id=id; js.src=b+"embed.js"; q=gt.call(d,"script")[0]; q.parentNode.insertBefore(js,q) } })() </script>
                    <p class="caption" style="text-align:left;">¿No carga el formulario? Escríbenos directamente a <a href="mailto:parroquisantateresabarcelona@gmail.com">parroquisantateresabarcelona@gmail.com</a>.</p>
                    <div class="data-notice">
                        <strong>Información básica sobre protección de datos</strong>
                        <p><b>Responsable:</b> Parroquia de Santa Teresa de Jesús. <b>Finalidad:</b> atender tu consulta. <b>Legitimación:</b> tu consentimiento. <b>Destinatarios:</b> no se ceden datos a terceros, salvo obligación legal; el formulario lo presta Typeform. <b>Derechos:</b> acceso, rectificación, supresión y otros, escribiendo a nuestro correo. <a href="privacidad.html">Más información en la Política de privacidad</a>.</p>
                    </div>
                </div>
                <div>
                    <span class="subtitulo text-left">¿Dónde estamos?</span>
                    <h2 class="text-left">Visítanos</h2>
                    <hr class="section-divider" style="margin-left:0;">
                    <div class="embed-frame">
                        <iframe title="Mapa de la Parroquia Santa Teresa de Jesús" height="536" loading="lazy" allowfullscreen
                            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d11966.759774653801!2d2.1558072908873487!3d41.42424881242464!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12a4bd4d9ae3237b%3A0xd805a433a983f974!2sParr%C3%B2quia+Santa+Teresa+de+Jes%C3%BAs!5e0!3m2!1sca!2ses!4v1555520866181!5m2!1sca!2ses"></iframe>
                    </div>
                </div>
            </div>
        </section>
""")

# ---------------------------------------------------------------- MISAS
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
                    <ul><li>11:00 h — Eucaristía</li><li>13:00 h — Eucaristía</li></ul>
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
                    <span class="subtitulo">Agrégalo a tu calendario</span>
                    <h2>Calendario de eucaristías y actividades</h2>
                    <hr class="section-divider">
                    <div class="embed-frame">
                        <iframe title="Calendario de eucaristías y actividades" height="520" loading="lazy" scrolling="no"
                            src="https://calendar.google.com/calendar/embed?title=Agrega%20a%20tu%20calendario%20el%20horario%20de%20eucaristías%20y%20actividades&amp;height=600&amp;wkst=1&amp;bgcolor=%23ffffff&amp;src=6ufb6ib57o0aq9m4l4gnk9lkng%40group.calendar.google.com&amp;color=%2342104A&amp;ctz=Europe%2FMadrid&amp;mode=AGENDA"></iframe>
                    </div>
                </div>
            </div>
        </section>
""")

# ---------------------------------------------------------------- SACRAMENTOS
PAGES["html/adminsacra.html"] = page(1, "Sacramentos", "Sacramento del Perdón, bautizos, confirmación y despacho parroquial en la Parroquia Santa Teresa de Jesús.", body=page_hero("Administración de", "Sacramentos", "web/img_5434.jpg", pos="center 85%") + """
        <section>
            <div class="section-head">
                """ + ORNAMENT + """
                <span class="subtitulo">Cuándo y cómo</span>
                <h2>Celebrar los sacramentos</h2>
                <p>Te acompañamos en los momentos más importantes de la vida cristiana.</p>
            </div>
            <div class="icon-grid">
""" + "\n".join([
    icon_card("manos", "Perdón", "Mn. Sols administra el sacramento del Perdón de manera fija los sábados de 18:30 a 19:00 horas y siempre un rato antes de cada misa.", "misas.html"),
    icon_card("agua", "Bautismo", "Hay ceremonias bautismales al mediodía en cualquier domingo del año que se pida.", "contacto.html"),
    icon_card("paloma", "Confirmación", "Cada tres años se celebra la Confirmación. La catequesis prepara a los adolescentes a partir de los 14 años.", "catequesis.html"),
    icon_card("anillos", "Matrimonio", "Para bodas y su preparación, consulta en el despacho parroquial los viernes por la tarde.", "contacto.html"),
]) + """
            </div>
        </section>

        <section class="section-warm" id="despacho">
            <div class="two-col center">
                <div class="framed-img">
                    <img src="../fotosdefinitivas/web/img_5434.jpg" alt="Celebración de la eucaristía" loading="lazy">
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
                <div class="icon-card">
                    <div class="icon-circle">""" + SAC_ICONS["caliz"] + """</div>
                    <h3>Primera comunión</h3>
                    <p>Preparación de los niños para recibir por primera vez el sacramento de la eucaristía.</p>
                </div>
                <div class="icon-card">
                    <div class="icon-circle">""" + SAC_ICONS["paloma"] + """</div>
                    <h3>Confirmación</h3>
                    <p>Para adolescentes a partir de los 14 años. Cada tres años se celebra la Confirmación en la parroquia.</p>
                </div>
            </div>
        </section>

        <section class="section-warm">
            <div class="section-head" style="margin-bottom:2rem;">
                <span class="subtitulo">Inscripciones</span>
                <h2>Inscríbete a las comuniones del próximo curso</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="embed-frame" style="max-width:760px; margin:0 auto;">
                <iframe title="Formulario de inscripción a la catequesis" height="1170" loading="lazy"
                    src="https://docs.google.com/forms/d/e/1FAIpQLSeCFdrkvI7w7rS46NBc6cYaN5BYVMH_pc0huZAPHk1Q-MiCXQ/viewform?embedded=true">Cargando…</iframe>
            </div>
            <div class="data-notice" style="max-width:760px; margin:1.5rem auto 0;">
                <strong>Información básica sobre protección de datos</strong>
                <p><b>Responsable:</b> Parroquia de Santa Teresa de Jesús. <b>Finalidad:</b> gestionar la inscripción y la participación en la catequesis. <b>Legitimación:</b> consentimiento del padre, madre o tutor legal (los datos de menores de 14 años solo pueden facilitarlos ellos). <b>Destinatarios:</b> no se ceden a terceros, salvo obligación legal; el formulario lo presta Google. <b>Derechos:</b> acceso, rectificación, supresión y otros, escribiendo a nuestro correo. <a href="privacidad.html">Más información en la Política de privacidad</a>.</p>
            </div>
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
                        <a href="https://mega.nz/#F!mkNRDaKA!9RB9WIL2ftWbm_vEexp94g" class="btn" target="_blank" rel="noopener">Fotografías de la Eucaristía dominical</a>
                        <a href="https://mega.nz/#F!TptljabY!fkMjK3iNmVxgv42GxhD-Wg" class="btn" target="_blank" rel="noopener">Fotografías del Domingo de Ramos 2019</a>
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
                    <a class="reading-next" href="{o["slug"]}.html">
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


def archive_body():
    if not HOMILIAS:
        return ""
    top = HOMILIAS[0]
    quote = _first_quote(top.get("texto"))
    featured = f"""
            <article class="reflection-featured">
                <a class="rf-photo" href="reflexiones/{top["slug"]}.html" aria-hidden="true" tabindex="-1">
                    {_portrait(top, 1)}
                    {date_badge(top)}
                </a>
                <div class="rf-body">
                    <span class="rf-tag"><span class="notice-dot" aria-hidden="true"></span>Última reflexión</span>
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
                <li class="rf-row" data-author="{esc(h["autor_nombre"])}">
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
                    <a href="contacto.html" class="btn btn-solid">Quiero apuntarme</a>
                    <a href="https://www.instagram.com/parroquiasantateresadejesusbcn/" class="btn" target="_blank" rel="noopener">Síguenos en Instagram</a>
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
PAGES["html/noticias.html"] = page(1, "Noticias", "Noticias del Vaticano y del Arzobispado de Barcelona, actualizadas cada día, en la web de la Parroquia Santa Teresa de Jesús.", active="noticias", extra_head=NEWS_HEAD_1, body=page_hero("Actualidad de la Iglesia", "Noticias", "web/dsc_0541.jpg") + """
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

        <section class="section-warm">
            <div class="section-head" style="margin-bottom:2.5rem;">
                <span class="subtitulo">De nuestra parroquia</span>
                <h2>Reflexiones y homilías</h2>
                <hr class="section-divider" style="margin-bottom:0;">
            </div>
            <div class="reflection-list">""" + "".join(f"""
                <a class="reflection-card" href="reflexiones/{h["slug"]}.html">
                    {_portrait(h, 1)}
                    <span class="book-kicker">{esc(h["autor_nombre"])}</span>
                    <h3>{esc(h["titulo"])}</h3>
                    <span class="flip-hint">Leer &rarr;</span>
                </a>""" for h in HOMILIAS[:3]) + """
            </div>
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
                        <tr><td>Chat de atención</td><td>Tawk.to Inc. (EE. UU.)</td><td>Todas las páginas</td><td>Chat en directo con la parroquia. <a href="https://www.tawk.to/privacy-policy/" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>Google Maps, Calendar y Forms</td><td>Google Ireland Ltd.</td><td>Contacto, Eucaristías, Catequesis</td><td>Mapa, calendario y formulario de inscripción. <a href="https://policies.google.com/technologies/cookies?hl=es" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>YouTube (modo de privacidad mejorada)</td><td>Google Ireland Ltd.</td><td>Imágenes y vídeos</td><td>Reproducir vídeos. <a href="https://policies.google.com/privacy?hl=es" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>Instagram</td><td>Elfsight LLC / Meta Platforms Ireland Ltd.</td><td>Inicio</td><td>Mostrar publicaciones de nuestro Instagram. <a href="https://elfsight.com/privacy-policy/" target="_blank" rel="noopener">Política</a></td></tr>
                        <tr><td>Typeform</td><td>Typeform S.L. (España)</td><td>Contacto</td><td>Formulario de contacto. <a href="https://www.typeform.com/help/a/typeform-cookies-360042093071/" target="_blank" rel="noopener">Política</a></td></tr>
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
                        <tr><td>Formulario de inscripción a la catequesis</td><td>Datos del menor y de su padre, madre o tutor</td><td>Gestionar la inscripción y la catequesis</td><td>Consentimiento del padre, madre o tutor (art. 6.1.a RGPD y art. 7 LOPDGDD) y actividad legítima de una entidad religiosa con sus fieles (art. 9.2.d RGPD)</td></tr>
                        <tr><td>Chat de atención</td><td>Nombre, correo y mensajes que escribas</td><td>Atender tu consulta en directo</td><td>Tu consentimiento (art. 6.1.a RGPD)</td></tr>
                        <tr><td>Fotografías de actividades</td><td>Imagen de las personas que aparecen</td><td>Dar a conocer la vida de la parroquia</td><td>Consentimiento de los interesados o de sus representantes legales</td></tr>
                    </tbody>
                </table></div>
                <p>Los datos de <strong>menores de 14 años</strong> solo pueden facilitarlos sus padres o tutores legales.</p>

                <h3>3. Cuánto tiempo los conservamos</h3>
                <p>Los datos de contacto y del chat, el tiempo necesario para atender tu consulta. Los de catequesis, mientras dure la formación y, después, durante los plazos que exija la normativa civil o canónica aplicable. En cualquier caso, mientras no solicites su supresión cuando proceda.</p>

                <h3>4. Destinatarios</h3>
                <p>No cedemos datos a terceros salvo obligación legal. Para prestar algunos servicios usamos proveedores que tratan datos por nuestra cuenta (encargados del tratamiento): Google (formularios, calendario y mapas), Typeform (formulario de contacto) y Tawk.to (chat). Algunos están en Estados Unidos; las transferencias se amparan en el Marco de Privacidad de Datos UE-EE. UU. cuando el proveedor está adherido o, en su defecto, en las cláusulas contractuales tipo aprobadas por la Comisión Europea.</p>

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
LANGS = ["es", "ca", "en"]
LOCALES = {"es": "es_ES", "ca": "ca_ES", "en": "en_GB"}
LANG_NAMES = [("es", "ES", "Español"), ("ca", "CA", "Català"), ("en", "EN", "English")]
HOMILY_NOTE = {"ca": "Text original en castellà.", "en": "Original text in Spanish."}


def out_path(lang, rel):
    return rel if lang == "es" else f"{lang}/{rel}"


def page_url(lang, rel):
    p = out_path(lang, rel)
    if p.endswith("index.html"):
        return SITE + p[:-len("index.html")]
    return SITE + (p[:-len(".html")] if p.endswith(".html") else p)


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
    "es": ("Horarios de misa", "Laborables y sábados · 19:00 h", "Domingos · 11:00 y 13:00 h", "Idioma"),
    "ca": ("Horaris de missa", "Feiners i dissabtes · 19:00 h", "Diumenges · 11:00 i 13:00 h", "Idioma"),
    "en": ("Mass times", "Weekdays and Saturdays · 19:00", "Sundays · 11:00 and 13:00", "Language"),
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
    html = re.sub(r'((?:href|src|data-src)=")((?:\.\./)*)(css/|js/|fotosdefinitivas/|fonts/|data/|favicon|apple-touch-icon|site\.webmanifest)',
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
            if rel.startswith("html/reflexiones/"):
                # reflexión subida desde el panel: si su texto aún no está traducido, se muestra
                # en castellano con un aviso (sin contarla como texto pendiente del generador)
                _art = re.search(r'<article class="prose.*?</article>', html, re.S)
                _pend = _art and any(k not in TABLE for k in i18n.extract(_art.group(0), rel))
                html = i18n.translate(html, rel, lang, TABLE, set())
                if _pend:
                    html = html.replace('<article class="prose', f'<p class="lang-note">{HOMILY_NOTE[lang]}</p>\n                <article class="prose', 1)
            else:
                html = i18n.translate(html, rel, lang, TABLE, missing)
            html = html.replace('<html lang="es">', f'<html lang="{lang}">', 1)
            html = relocate_assets(html)
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
