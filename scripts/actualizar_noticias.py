"""Descarga las últimas noticias de Vatican News y del Arzobispado de Barcelona
y las guarda en data/noticias.js para que la web las muestre.

Lo ejecuta cada día GitHub Actions (.github/workflows/noticias.yml).
Solo usa la biblioteca estándar de Python. Uso manual:  python scripts/actualizar_noticias.py
"""
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "data", "noticias.js")
POR_FUENTE = 8
UA = "Mozilla/5.0 (compatible; ParroquiaSantaTeresaBCN/1.0; +https://www.parroquiasantateresabcn.org/)"

FUENTES = {
    "vaticano_es": ("rss", "https://www.vaticannews.va/es.rss.xml"),
    "vaticano_en": ("rss", "https://www.vaticannews.va/en.rss.xml"),
    "arzobispado_ca": ("wp", "https://esglesia.barcelona/wp-json/wp/v2/ebn-actualitat"),
    "arzobispado_es": ("wp", "https://esglesia.barcelona/es/wp-json/wp/v2/ebn-actualitat"),
}


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def texto_plano(s, limite=190):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > limite:
        s = s[:limite].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return s


def leer_rss(url):
    root = ET.fromstring(descargar(url))
    items = []
    for it in root.iter("item"):
        fecha = it.findtext("pubDate")
        try:
            fecha = parsedate_to_datetime(fecha).astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError):
            fecha = None
        items.append({
            "titulo": texto_plano(it.findtext("title"), 160),
            "enlace": (it.findtext("link") or "").strip(),
            "fecha": fecha,
            "resumen": texto_plano(it.findtext("description")),
        })
    return items


def leer_wp(url):
    datos = json.loads(descargar(url + "?per_page=%d&_fields=date_gmt,link,title,excerpt" % POR_FUENTE))
    return [{
        "titulo": texto_plano(p["title"]["rendered"], 160),
        "enlace": p["link"],
        "fecha": p.get("date_gmt", "") + "+00:00" if p.get("date_gmt") else None,
        "resumen": texto_plano(p.get("excerpt", {}).get("rendered", "")),
    } for p in datos]


def main():
    anterior = {}
    if os.path.exists(SALIDA):  # si una fuente falla, se conservan sus noticias anteriores
        try:
            anterior = json.loads(open(SALIDA, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))
        except (ValueError, IndexError):
            anterior = {}

    resultado = {"actualizado": datetime.now(timezone.utc).isoformat(timespec="minutes")}
    errores = 0
    for clave, (tipo, url) in FUENTES.items():
        try:
            items = leer_rss(url) if tipo == "rss" else leer_wp(url)
            resultado[clave] = [i for i in items if i["titulo"] and i["enlace"].startswith("https://")][:POR_FUENTE]
            print(f"{clave}: {len(resultado[clave])} noticias")
        except Exception as e:  # noqa: BLE001 - registrar y seguir con las demás fuentes
            errores += 1
            resultado[clave] = anterior.get(clave, [])
            print(f"{clave}: ERROR {e} (se mantienen {len(resultado[clave])} anteriores)", file=sys.stderr)

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8", newline="\n") as f:
        f.write("/* Generado automáticamente por scripts/actualizar_noticias.py. No editar a mano. */\n")
        f.write("window.NOTICIAS = " + json.dumps(resultado, ensure_ascii=False, indent=1) + ";\n")
    return 1 if errores == len(FUENTES) else 0


if __name__ == "__main__":
    sys.exit(main())
