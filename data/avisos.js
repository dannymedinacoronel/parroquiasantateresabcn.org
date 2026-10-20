/* ==========================================================================
   AVISOS DE LA PARROQUIA
   Al entrar en la web se muestra el primer aviso activo de esta lista,
   en una tarjeta abajo a la derecha (en el móvil, desde abajo).

   CÓMO AÑADIR UN AVISO NUEVO
   1. Copia un bloque { ... } y ponlo el PRIMERO de la lista.
   2. Cambia el "id" por uno nuevo (si repites un id ya cerrado, no se verá).
   3. Rellena los textos en castellano (es), catalán (ca) e inglés (en).
   4. "enlace": página a la que lleva el botón, sin "../" (p. ej. "html/humilias.html").
   5. "desde" y "hasta" (AAAA-MM-DD) limitan las fechas en que se muestra.
      Déjalos vacíos ("") para que se vea siempre.
   6. "imagen" es opcional: una foto de fotosdefinitivas/web/.

   Cada visitante ve cada aviso una sola vez: al cerrarlo o pulsar el botón
   ya no vuelve a aparecerle.
   ========================================================================== */
window.AVISOS = [
    {
        id: "reflexiones-2026-10",
        desde: "2026-10-20",
        hasta: "2026-12-31",
        imagen: "fotosdefinitivas/web/magdalena-retrato.jpg",
        enlace: "html/humiliasmagdalena3domingo.html",
        etiqueta: { es: "Ya disponible", ca: "Ja disponible", en: "Now available" },
        titulo: {
            es: "Reflexiones del Evangelio",
            ca: "Reflexions de l'Evangeli",
            en: "Gospel reflections"
        },
        texto: {
            es: "Escucha la reflexión «Remar mar adentro» de Magdalena, ahora con el audio restaurado, y lee también la de Mn. Albert Sols.",
            ca: "Escolta la reflexió «Remar mar endins» de la Magdalena, ara amb l'àudio restaurat, i llegeix també la de Mn. Albert Sols.",
            en: "Listen to Magdalena's reflection «Put out into the deep», now with restored audio, and read Fr Albert Sols' reflection too."
        },
        boton: { es: "Leer y escuchar", ca: "Llegir i escoltar", en: "Read and listen" }
    }
];
