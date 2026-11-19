"""Páginas hechas con el editor visual (Puck, en /admin/editor/).

Cada página es un JSON en contenido/paginas/<slug>.json con una lista de bloques. Cada tipo de bloque tiene
UNA plantilla en editor/plantillas/<Tipo>.html, que usan a la vez el editor (editor/tpl.js) y este archivo:
así lo que se ve al editar y lo que se publica sale del mismo sitio.

Plantillas (un «mustache» pequeño, igual en editor/tpl.js):
  {{campo}}            texto escapado            {{{campo}}}        HTML tal cual
  {{campo|filtro}}     filtro: p (párrafos), br (saltos de línea), img (foto), url (enlace), icon (icono), count, yt (vídeo de YouTube)
  {{#lista}}…{{/lista}}  repite por cada elemento (dentro: @index, @first, @last); con un valor, se muestra si no está vacío
  {{^campo}}…{{/campo}}  se muestra si el campo está vacío
  {{#campo=valor}}…{{/campo=valor}}  se muestra si el campo vale eso
  {{#lista?}}…{{/lista?}}  se muestra una sola vez si la lista (o el campo) no está vacío

Traducciones: junto a cada texto puede haber «<campo>_tr»: {"ca": "...", "en": "..."}. Se añaden a la tabla de
traducciones de la web; si no hay, sale el castellano (o la traducción que ya tuviera la tabla).
"""
import html as _html
import json
import os
import re

TAG = re.compile(r"\{\{(\{?)([#^/]?)\s*([^}]+?)\s*\}?\}\}")


def esc(v):
    return _html.escape("" if v is None else str(v), quote=False).replace('"', "&quot;")


def parse(tpl):
    """Plantilla -> árbol: lista de str y tuplas (tipo, nombre, hijos)."""
    root, stack, pos = [], [], 0
    cur = root
    for m in TAG.finditer(tpl):
        if m.start() > pos:
            cur.append(tpl[pos:m.start()])
        raw, kind, name = m.group(1), m.group(2), m.group(3).strip()
        pos = m.end()
        if kind in ("#", "^"):
            node = (kind, name, [])
            cur.append(node)
            stack.append((cur, name))
            cur = node[2]
        elif kind == "/":
            parent, opened = stack.pop()
            assert opened == name, f"plantilla: se cierra {name} pero estaba abierto {opened}"
            cur = parent
        else:
            cur.append(("raw" if raw else "var", name, None))
    if pos < len(tpl):
        cur.append(tpl[pos:])
    assert not stack, "plantilla: falta cerrar " + ", ".join(n for _, n in stack)
    return root


def lookup(stack, name):
    for ctx in reversed(stack):
        if isinstance(ctx, dict) and name in ctx:
            return ctx[name]
    return ""


def truthy(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return True
    return bool(v)


class Renderer:
    def __init__(self, filters, globals_):
        self.filters = filters
        self.globals = globals_
        self.cache = {}

    def tree(self, tpl):
        if tpl not in self.cache:
            self.cache[tpl] = parse(tpl)
        return self.cache[tpl]

    def value(self, stack, expr):
        name, _, flt = expr.partition("|")
        v = lookup(stack, name.strip())
        if flt:
            return self.filters[flt.strip()](v, stack)
        return v

    def run(self, nodes, stack):
        out = []
        for n in nodes:
            if isinstance(n, str):
                out.append(n)
                continue
            kind, name, kids = n
            if kind == "var":
                v = self.value(stack, name)
                out.append(v if "|" in name else esc(v))
            elif kind == "raw":
                out.append(str(self.value(stack, name) or ""))
            else:
                if "=" in name:
                    k, _, want = name.partition("=")
                    show = str(lookup(stack, k.strip())) == want.strip()
                    if (kind == "#") == show:
                        out.append(self.run(kids, stack))
                    continue
                if name.endswith("?"):
                    v = lookup(stack, name[:-1])
                    show = truthy(v) and not (isinstance(v, list) and not v)
                    if (kind == "#") == show:
                        out.append(self.run(kids, stack))
                    continue
                v = lookup(stack, name)
                if kind == "^":
                    if not truthy(v) or (isinstance(v, list) and not v):
                        out.append(self.run(kids, stack))
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        meta = {"@i": i, "@index": i + 1, "@first": i == 0, "@last": i == len(v) - 1}
                        out.append(self.run(kids, stack + [meta, item if isinstance(item, dict) else {".": item}]))
                elif isinstance(v, dict):
                    out.append(self.run(kids, stack + [v]))
                elif truthy(v):
                    out.append(self.run(kids, stack))
        return "".join(out)

    def render(self, tpl, props):
        return self.run(self.tree(tpl), [self.globals, props])


# ------------------------------------------------------------------ filtros (iguales en editor/tpl.js)
def make_filters(base, icons, img_url=None, hero_url=None):
    def img(v, _s=None):
        v = str(v or "").strip()
        if not v:
            return ""
        if re.match(r"^(https?:)?//|^/|^data:", v):
            return esc(v)
        return esc(base + "fotosdefinitivas/web/" + v)

    def url(v, _s=None):
        v = str(v or "").strip()
        if not v or re.match(r"^(https?:|mailto:|tel:|#|/)", v):
            return esc(v)
        return esc(base + v)

    def paras(v, _s=None):
        parts = [p.strip() for p in re.split(r"\n\s*\n", str(v or "")) if p.strip()]
        return "".join(f"<p>{esc(p).replace(chr(10), '<br>')}</p>" for p in parts)

    def br(v, _s=None):
        return esc(str(v or "").strip()).replace("\n", "<br>")

    def icon(v, _s=None):
        return icons.get(str(v or ""), "")

    def count(v, _s=None):
        v = str(v or "").strip()
        m = re.fullmatch(r"(\+?)(\d+)", v)
        if not m:
            return ""
        n = int(m.group(2))
        return f' data-count="{n}"' + (' data-prefix="+"' if m.group(1) else "") + (' data-from="1850"' if 1850 < n < 2100 else "")

    def yt(v, _s=None):
        v = str(v or "").strip()
        m = re.search(r"(?:youtu\.be/|v=|embed/|shorts/)([A-Za-z0-9_-]{11})", v)
        return esc(m.group(1) if m else v if re.fullmatch(r"[A-Za-z0-9_-]{11}", v) else "")

    return {"yt": yt, "img": img_url or img, "hero": hero_url or img_url or img, "url": url, "p": paras, "br": br, "icon": icon, "count": count}


# ------------------------------------------------------------------ páginas
HERE = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)), "editor", "plantillas")


def load_templates():
    out = {}
    for f in sorted(os.listdir(TPL_DIR)):
        if f.endswith(".html"):
            with open(os.path.join(TPL_DIR, f), encoding="utf-8") as fh:
                out[f[:-5]] = fh.read()
    return out


def _segments(t):
    return [s.strip() for s in re.split(r"\n+", str(t or "")) if s.strip()]


def translations(data):
    """[(es, ca, en)] con lo que se haya escrito en los campos «Traducción» de cada bloque."""
    out, seen = [], set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                tr = o.get(k + "_tr")
                if isinstance(v, str) and isinstance(tr, dict) and (tr.get("ca") or tr.get("en")):
                    es_s, ca_s, en_s = _segments(v), _segments(tr.get("ca")), _segments(tr.get("en"))
                    for i, e in enumerate(es_s):
                        c = ca_s[i] if len(ca_s) == len(es_s) else ""
                        n = en_s[i] if len(en_s) == len(es_s) else ""
                        key = esc(e)
                        if key not in seen:
                            seen.add(key)
                            out.append((key, esc(c) if c else "", esc(n) if n else ""))
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(data)
    return out


def spanish_texts(data):
    """Todos los textos en castellano de la página (para no contarlos como «sin traducir»)."""
    out = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.endswith("_tr") or k in ("id", "type"):
                    continue
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
        elif isinstance(o, str):
            out.update(esc(s) for s in _segments(o))
    walk(data)
    return out


def load_page(root, slug):
    path = os.path.join(root, "contenido", "paginas", slug + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def render_page(data, renderer, templates, auto):
    """HTML de todos los bloques. Los automáticos (horario, agenda…) los pone el generador con `auto`."""
    out = []
    for block in data.get("content", []):
        t, props = block.get("type"), block.get("props") or {}
        if props.get("oculto"):
            continue
        if t in auto:
            out.append(auto[t]())
        elif t in templates:
            out.append(renderer.render(templates[t], props))
        else:
            print("AVISO: bloque desconocido en el editor visual:", t)
    return re.sub(r' data-(?:f="[^"]*"|multi|bgf)(?=[\s>])', "", "\n".join(out))
