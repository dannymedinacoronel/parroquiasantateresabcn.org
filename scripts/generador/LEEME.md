# Generador de la web

Todas las páginas (`index.html`, `html/`, `ca/`, `en/`, `404.html`, `sitemap.xml`, `robots.txt`)
se generan con este script. Para cambiar un texto o una página, edita `generar_web.py`
(contenido en castellano) y `translations.py` (catalán e inglés), y ejecuta desde la raíz:

    python scripts/generador/generar_web.py .

El script avisa de los textos que falten por traducir.
Las noticias se actualizan solas con `scripts/actualizar_noticias.py` (GitHub Actions, cada día).
