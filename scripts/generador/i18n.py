"""Traducción de las páginas generadas (es) a ca / en mediante una tabla de frases."""
import re

SKIP_BLOCKS = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S)
HOMILY_PAGES = ("html/humilias.html", "html/humiliasmagdalena3domingo.html")
ATTRS = ("alt", "title", "aria-label", "placeholder", "data-service")
META_RE = re.compile(r'(<meta (?:name="description"|property="og:(?:title|description)") content=")([^"]*)(")')


def _protect(html, rel):
    """Devuelve (html_sin_bloques, lista_bloques) para no tocar scripts, estilos ni el texto de las homilías."""
    blocks = []

    def keep(m):
        blocks.append(m.group(0))
        return f"\x00{len(blocks) - 1}\x00"
    html = SKIP_BLOCKS.sub(keep, html)
    return html, blocks


def _restore(html, blocks):
    return re.sub(r"\x00(\d+)\x00", lambda m: blocks[int(m.group(1))], html)


def _is_text(s):
    if re.fullmatch(r"(&\w+;\s*)+|__[A-Z_]+__", s):   # entidades (&copy;, &rarr;) y marcadores internos
        return False
    return bool(re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]", s)) and not s.startswith(("http", "@parroquia"))


def extract(html, rel):
    html, _ = _protect(html, rel)
    out = []
    for m in re.finditer(r">([^<>]+)<", html):
        t = m.group(1).strip()
        if _is_text(t):
            out.append(t)
    for a in ATTRS:
        for m in re.finditer(r'\s%s="([^"]+)"' % a, html):
            if _is_text(m.group(1)):
                out.append(m.group(1))
    for m in META_RE.finditer(html):
        out.append(m.group(2))
    return out


def translate(html, rel, lang, table, missing):
    html, blocks = _protect(html, rel)

    def tr(s):
        key = s.strip()
        if not _is_text(key):
            return s
        entry = table.get(key)
        if not entry or not entry.get(lang):
            missing.add(key)
            return s
        lead = s[:len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()):]
        return lead + entry[lang] + trail

    html = re.sub(r">([^<>]+)<", lambda m: ">" + tr(m.group(1)) + "<", html)
    for a in ATTRS:
        html = re.sub(r'(\s%s=")([^"]+)(")' % a, lambda m: m.group(1) + tr(m.group(2)) + m.group(3), html)
    html = META_RE.sub(lambda m: m.group(1) + tr(m.group(2)) + m.group(3), html)
    return _restore(html, blocks)
