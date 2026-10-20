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

   SI LA LISTA ESTÁ VACÍA (lo normal): la web muestra sola un aviso con la
   ÚLTIMA REFLEXIÓN publicada desde el panel, con la etiqueta «Nueva
   reflexión» durante sus primeros 30 días. Al publicar otra, el aviso cambia
   y vuelve a salir a todos los visitantes. Un aviso escrito aquí tiene
   prioridad sobre el automático mientras esté activo.

   Ejemplo de aviso escrito a mano:
    {
        id: "fiesta-2026",
        desde: "2026-10-01", hasta: "2026-10-15",
        imagen: "fotosdefinitivas/web/santateresa.jpg",
        enlace: "html/contacto.html",
        etiqueta: { es: "Fiesta", ca: "Festa", en: "Feast" },
        titulo: { es: "Fiesta de Santa Teresa", ca: "Festa de Santa Teresa", en: "Feast of Saint Teresa" },
        texto: { es: "...", ca: "...", en: "..." },
        boton: { es: "Más información", ca: "Més informació", en: "More information" }
    }
   ========================================================================== */
window.AVISOS = [];
