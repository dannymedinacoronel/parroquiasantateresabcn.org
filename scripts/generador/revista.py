"""Revista digital de la parroquia: números y artículos escritos desde el panel (Decap CMS).

contenido/revista/numeros/<slug>.json    un número de la revista
    titulo, numero, fecha, portada, portada_completa, presentacion, pdf, enlace, publicado
contenido/revista/articulos/<slug>.json  un artículo, asignado a un número por su slug
    numero, titulo, seccion, autor, entradilla, foto, pie, texto, orden, publicado

Un número solo sale en la web cuando está marcado como «Publicado»; un artículo, cuando su
número está publicado y él no está desmarcado como «Listo para publicar».
"""
import glob
import json
import os
import re


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh) or {}
    except ValueError as e:
        print("AVISO: no se pudo leer", os.path.basename(path), e)
        return None


def media(root, value):
    """Archivo subido desde el panel («/fotosdefinitivas/...») → ruta desde la raíz, si existe."""
    v = (value or "").strip()
    if not v:
        return ""
    if re.match(r"^(https?:)?//", v):
        return v
    v = v.lstrip("/")
    return v if os.path.exists(os.path.join(root, v)) else ""


def _int(value, default=None):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def load(root, hom):
    """Números publicados (el más reciente primero), cada uno con sus artículos ordenados."""
    base = os.path.join(root, "contenido", "revista")
    numeros = {}
    for path in sorted(glob.glob(os.path.join(base, "numeros", "*.json"))):
        n = _read(path)
        if not n or not (n.get("titulo") or "").strip() or n.get("publicado") is not True:
            continue
        if hom.PENDIENTE.search((n.get("titulo") or "") + (n.get("presentacion") or "")):
            print("AVISO: no se publica el número", os.path.basename(path), "- aún tiene huecos [entre corchetes]")
            continue
        slug = os.path.splitext(os.path.basename(path))[0]
        n.update(
            slug=slug,
            url=f"html/revista/{slug}.html",
            fecha=(n.get("fecha") or "")[:10],
            num=_int(n.get("numero")),
            portada=media(root, n.get("portada")),
            pdf=media(root, n.get("pdf")),
            enlace=(n.get("enlace") or "").strip(),
            extracto=hom.first_paragraph(n.get("presentacion", "")),
            articulos=[],
        )
        numeros[slug] = n
    for path in sorted(glob.glob(os.path.join(base, "articulos", "*.json"))):
        a = _read(path)
        if not a or not (a.get("titulo") or "").strip() or a.get("publicado") is False:
            continue
        n = numeros.get((a.get("numero") or "").strip())
        if not n:
            continue  # su número no existe o aún es un borrador
        if hom.PENDIENTE.search((a.get("titulo") or "") + (a.get("texto") or "")):
            print("AVISO: no se publica el artículo", os.path.basename(path), "- aún tiene huecos [entre corchetes]")
            continue
        slug = os.path.splitext(os.path.basename(path))[0]
        a.update(
            slug=slug,
            url=f"html/revista/{n['slug']}--{slug}.html",
            foto=media(root, a.get("foto")),
            orden=_int(a.get("orden"), 999),
            extracto=(a.get("entradilla") or "").strip() or hom.first_paragraph(a.get("texto", "")),
        )
        n["articulos"].append(a)
    for n in numeros.values():
        n["articulos"].sort(key=lambda a: (a["orden"], a["titulo"].lower()))
    return sorted(numeros.values(), key=lambda n: (n["fecha"], n["num"] or 0), reverse=True)
