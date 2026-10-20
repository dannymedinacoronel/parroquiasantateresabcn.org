"""Lectura de las homilías y autores publicados desde el panel (contenido/*.json)
y conversión del texto (Markdown sencillo) a HTML.

Markdown admitido en el texto:
  párrafos separados por una línea en blanco      ·  salto de línea simple -> <br>
  ### Subtítulo                                   ·  - elemento de lista  (o * elemento)
  > Frase destacada (cita grande)                 ·  **negrita**  y  *cursiva* / _cursiva_
"""
import glob
import html
import json
import os
import re
from datetime import date

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def _inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", t)
    return t


def markdown(text, indent="                    "):
    """Convierte el texto del panel en el HTML de la página de lectura."""
    text = (text or "").replace("\r\n", "\n").strip()
    out, first_p = [], True
    for block in re.split(r"\n\s*\n", text):
        lines = [l.rstrip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        if lines[0].startswith("#"):
            out.append(f"{indent}<h3>{_inline(lines[0].lstrip('#').strip())}</h3>")
        elif all(re.match(r"^[-*]\s+", l) for l in lines):
            items = "".join(f"\n{indent}    <li>{_inline(re.sub(r'^[-*]\s+', '', l))}</li>" for l in lines)
            out.append(f"{indent}<ul>{items}\n{indent}</ul>")
        elif all(l.startswith(">") for l in lines):
            q = " ".join(l.lstrip(">").strip() for l in lines)
            out.append(f'{indent}<blockquote class="pull">{_inline(q)}</blockquote>')
        else:
            body = "<br>".join(_inline(l.strip()) for l in lines)
            cls = ' class="illuminated"' if first_p else ""
            first_p = False
            out.append(f"{indent}<p{cls}>{body}</p>")
    return "\n".join(out)


def first_paragraph(text):
    for block in re.split(r"\n\s*\n", (text or "").strip()):
        b = block.strip()
        if b and not b.startswith(("#", ">", "-", "* ")):
            return re.sub(r"\*\*|__", "", b.replace("\n", " "))
    return ""


def slugify(s):
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n"), ("ç", "c"), ("à", "a"), ("è", "e"), ("ò", "o"), ("ï", "i")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70] or "reflexion"


def fecha_larga(iso):
    try:
        d = date.fromisoformat(iso[:10])
        return f"{d.day} de {MESES[d.month - 1]} de {d.year}"
    except ValueError:
        return iso


def audio_src(value):
    """Acepta el número de pista de SoundCloud o su enlace completo."""
    v = (value or "").strip()
    if not v:
        return ""
    if v.isdigit():
        url = "https%3A//api.soundcloud.com/tracks/" + v
    else:
        v = v.split("?")[0]
        from urllib.parse import quote
        url = quote(v, safe="")
    return ("https://w.soundcloud.com/player/?url=" + url +
            "&color=%23bfa065&auto_play=false&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false")


def load(root):
    autores_path = os.path.join(root, "contenido", "autores.json")
    autores = {}
    if os.path.exists(autores_path):
        for a in json.load(open(autores_path, encoding="utf-8")).get("autores", []):
            if a.get("id"):
                autores[a["id"]] = a
    items = []
    for path in glob.glob(os.path.join(root, "contenido", "homilias", "*.json")):
        try:
            h = json.load(open(path, encoding="utf-8"))
        except ValueError as e:
            print("AVISO: no se pudo leer", os.path.basename(path), e)
            continue
        if not h.get("titulo") or h.get("publicado") is False:
            continue
        h["fecha"] = (h.get("fecha") or "")[:10]
        h["slug"] = os.path.splitext(os.path.basename(path))[0]
        h["url"] = f"html/reflexiones/{h['slug']}.html"
        a = autores.get(h.get("autor"), {})
        h["autor_nombre"] = a.get("nombre") or h.get("autor") or "Parroquia Santa Teresa de Jesús"
        h["autor_cargo"] = a.get("cargo", "")
        foto = (a.get("foto") or "").lstrip("/")
        h["autor_foto"] = foto if foto and os.path.exists(os.path.join(root, foto)) else ""
        h["kicker"] = (h.get("tiempo") or "").strip()
        h["extracto"] = first_paragraph(h.get("texto", ""))
        items.append(h)
    items.sort(key=lambda x: x["fecha"], reverse=True)
    return items, autores
