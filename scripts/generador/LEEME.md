# Generador de la web

Todas las páginas (`index.html`, `html/`, `ca/`, `en/`, `404.html`, `sitemap.xml`, `robots.txt`)
se generan con este script. Para cambiar un texto o una página, edita `generar_web.py`
(contenido en castellano) y `translations.py` (catalán e inglés), y ejecuta desde la raíz:

    python scripts/generador/generar_web.py .

El script avisa de los textos que falten por traducir.
Las noticias se actualizan solas con `scripts/actualizar_noticias.py` (GitHub Actions, cada día).

## Avisos al entrar en la web

Los avisos ("Ya disponible: …") se editan en `data/avisos.js`, sin tocar el generador.
El archivo explica cómo añadir uno: copiar un bloque, poner un `id` nuevo, los textos en
es/ca/en, el enlace y, si se quiere, las fechas `desde`/`hasta`. Cada visitante ve cada
aviso una sola vez.

## Traducciones de las reflexiones

Los textos de las homilías se traducen en `translations_homilias.py`. Al añadir una
reflexión nueva, el generador avisa de las frases que faltan por traducir.

## Panel de homilías (/admin/)

Las homilías y reflexiones se publican desde `https://www.parroquiasantateresabcn.org/admin/`
(Decap CMS). Cada una se guarda en `contenido/homilias/*.json` y las personas que escriben en
`contenido/autores.json`. Netlify ejecuta este generador en cada cambio (ver `netlify.toml`),
así que la reflexión aparece sola en la portada (la más reciente), en el menú, en el archivo
y con su página propia en `html/reflexiones/`.

Si una reflexión nueva no tiene traducción en `translations_homilias.py`, en catalán e inglés
se muestra en castellano con un aviso.
