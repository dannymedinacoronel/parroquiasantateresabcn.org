/* Parroquia Santa Teresa de Jesús — JavaScript común a todas las páginas */
(function () {
    /* Ruta a la página de cookies, relativa a este script (sirve desde / y desde /html) */
    var COOKIES_URL = document.currentScript
        ? document.currentScript.src.replace(/js\/site\.js.*$/, "html/cookies.html")
        : "html/cookies.html";

    var header = document.querySelector("header");

    /* --- Cabecera: transparente sobre la foto, blanca al hacer scroll --- */
    function onScroll() {
        header.classList.toggle("scrolled", window.scrollY > 40);
    }
    if (header) {
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });
    }

    /* --- Menú móvil --- */
    var hamburger = document.querySelector(".hamburger");
    var navMenu = document.querySelector(".nav-menu");

    function setMenu(open) {
        hamburger.classList.toggle("active", open);
        navMenu.classList.toggle("active", open);
        header.classList.toggle("menu-open", open);
        hamburger.setAttribute("aria-expanded", open ? "true" : "false");
        hamburger.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
        document.body.classList.toggle("menu-open", open);
    }

    if (hamburger && navMenu) {
        hamburger.addEventListener("click", function () {
            setMenu(!navMenu.classList.contains("active"));
        });
        navMenu.querySelectorAll(".nav-link").forEach(function (link) {
            link.addEventListener("click", function () { setMenu(false); });
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") setMenu(false);
        });
        window.addEventListener("resize", function () {
            if (window.innerWidth > 1024) setMenu(false);
        });
    }

    /* --- Tarjetas giratorias: clic / Enter para girar en móvil y teclado --- */
    document.querySelectorAll(".flip-card").forEach(function (card) {
        card.addEventListener("click", function (e) {
            if (e.target.closest("a")) return;
            card.classList.toggle("flipped");
        });
        card.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                card.classList.toggle("flipped");
            }
        });
    });

    /* --- Animación de entrada al hacer scroll --- */
    var revealSelector = [
        "main section:not(.hero):not(.page-hero) .section-head",
        "main section:not(.hero):not(.page-hero) > h2",
        ".two-col > *", ".card", ".feature", ".flip-card", ".widget-container",
        ".timeline-item", ".quote", ".image-band > *:not(.quote)", ".schedule-card",
        ".icon-card", ".mosaic a", ".info-cards", ".org-node", ".cta-band"
    ].join(",");
    var targets = document.querySelectorAll(revealSelector);
    if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in");
                    io.unobserve(entry.target);
                }
            });
        }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
        targets.forEach(function (el, i) {
            el.classList.add("reveal");
            /* pequeño escalonado entre elementos hermanos */
            var idx = Array.prototype.indexOf.call(el.parentNode.children, el);
            el.style.transitionDelay = Math.min(idx, 4) * 90 + "ms";
            io.observe(el);
        });
    }

    /* --- Próxima eucaristía (según los horarios fijos de la parroquia) --- */
    var MISAS = { 0: ["11:00", "13:00"], 1: ["19:00"], 2: ["19:00"], 3: ["19:00"], 4: ["19:00"], 5: ["19:00"], 6: ["19:00"] };
    var DIAS = ["el domingo", "el lunes", "el martes", "el miércoles", "el jueves", "el viernes", "el sábado"];
    document.querySelectorAll("[data-next-mass]").forEach(function (el) {
        var now = new Date();
        for (var off = 0; off < 8; off++) {
            var day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + off);
            var horas = MISAS[day.getDay()];
            for (var i = 0; i < horas.length; i++) {
                var hm = horas[i].split(":");
                var start = new Date(day.getFullYear(), day.getMonth(), day.getDate(), +hm[0], +hm[1]);
                var mins = (now - start) / 60000;
                var texto = null;
                if (mins >= 0 && mins < 50) {
                    texto = "Eucaristía <strong>en curso</strong> · comenzó a las " + horas[i];
                } else if (start > now) {
                    var cuando = off === 0 ? "hoy" : off === 1 ? "mañana" : DIAS[day.getDay()];
                    texto = "Próxima eucaristía: <strong>" + cuando + " a las " + horas[i] + " h</strong>";
                }
                if (texto) {
                    el.innerHTML = '<span class="dot" aria-hidden="true"></span><span>' + texto + "</span>";
                    el.hidden = false;
                    return;
                }
            }
        }
    });

    /* --- Galería: visor de fotos a pantalla completa --- */
    document.querySelectorAll(".mosaic").forEach(function (gallery) {
        var links = Array.prototype.slice.call(gallery.querySelectorAll("a"));
        if (!links.length) return;
        var box = document.createElement("div");
        box.className = "lightbox";
        box.setAttribute("role", "dialog");
        box.setAttribute("aria-modal", "true");
        box.setAttribute("aria-label", "Visor de fotos");
        box.innerHTML = '<img alt=""><button class="lb-close" aria-label="Cerrar">&times;</button>' +
            '<button class="lb-prev" aria-label="Anterior">&#8249;</button><button class="lb-next" aria-label="Siguiente">&#8250;</button>' +
            '<div class="lb-count"></div>';
        document.body.appendChild(box);
        var img = box.querySelector("img"), count = box.querySelector(".lb-count"), current = 0;

        function show(i) {
            current = (i + links.length) % links.length;
            img.src = links[current].href;
            img.alt = links[current].querySelector("img").alt;
            count.textContent = (current + 1) + " / " + links.length;
        }
        function close() { box.classList.remove("open"); document.body.classList.remove("menu-open"); }

        links.forEach(function (a, i) {
            a.addEventListener("click", function (e) {
                e.preventDefault();
                show(i);
                box.classList.add("open");
                document.body.classList.add("menu-open");
            });
        });
        box.querySelector(".lb-close").addEventListener("click", close);
        box.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
        box.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
        box.addEventListener("click", function (e) { if (e.target === box) close(); });
        document.addEventListener("keydown", function (e) {
            if (!box.classList.contains("open")) return;
            if (e.key === "Escape") close();
            if (e.key === "ArrowLeft") show(current - 1);
            if (e.key === "ArrowRight") show(current + 1);
        });
    });

    /* --- Año actual en el pie --- */
    document.querySelectorAll(".js-year").forEach(function (el) {
        el.textContent = new Date().getFullYear();
    });

    /* ======================================================================
       CONSENTIMIENTO DE COOKIES (LSSI art. 22.2 y Guía de cookies de la AEPD)
       - Nada de terceros se carga hasta que el visitante lo acepta.
       - "Aceptar" y "Rechazar" tienen el mismo peso visual.
       - La elección se guarda 12 meses y se puede cambiar desde el pie.
       ====================================================================== */
    var CONSENT_KEY = "pst-consent";
    var CONSENT_DAYS = 365;

    function readConsent() {
        try {
            var c = JSON.parse(localStorage.getItem(CONSENT_KEY));
            if (c && c.v === 1 && (Date.now() - c.date) < CONSENT_DAYS * 864e5) return c;
        } catch (e) { /* almacenamiento no disponible */ }
        return null;
    }
    function saveConsent(embeds, chat) {
        var c = { v: 1, date: Date.now(), embeds: !!embeds, chat: !!chat };
        try { localStorage.setItem(CONSENT_KEY, JSON.stringify(c)); } catch (e) { }
        return c;
    }

    /* Contenido externo: iframes y scripts bloqueados */
    var embedsLoaded = false;
    function loadEmbeds() {
        if (embedsLoaded) return;
        embedsLoaded = true;
        document.querySelectorAll("iframe[data-consent-src]").forEach(function (f) {
            f.src = f.getAttribute("data-consent-src");
            f.removeAttribute("data-consent-src");
        });
        document.querySelectorAll('script[type="text/plain"][data-consent="embeds"]').forEach(function (old) {
            var s = document.createElement("script");
            if (old.dataset.src) { s.src = old.dataset.src; s.async = true; }
            else { s.text = old.text; }
            old.parentNode.replaceChild(s, old);
        });
        document.querySelectorAll(".consent-embed").forEach(function (box) { box.classList.add("loaded"); });
    }

    /* Aviso dentro de cada contenido bloqueado, con botón para cargarlo */
    document.querySelectorAll(".consent-embed").forEach(function (box) {
        var ph = document.createElement("div");
        ph.className = "consent-placeholder";
        ph.innerHTML = '<p><strong>' + (box.dataset.service || "Contenido externo") + '</strong></p>' +
            '<p>Este contenido lo proporciona un servicio externo que puede instalar cookies. Solo se mostrará si lo aceptas.</p>' +
            '<button type="button" class="btn btn-solid">Aceptar y mostrar</button> ' +
            '<a href="' + COOKIES_URL + '">Más información</a>';
        ph.querySelector("button").addEventListener("click", function () {
            var c = readConsent() || {};
            apply(saveConsent(true, c.chat));
            hideBanner();
        });
        box.insertBefore(ph, box.firstChild);
    });

    /* Chat Tawk.to */
    var chatLoaded = false;
    function loadChat() {
        if (chatLoaded) return;
        chatLoaded = true;
        window.Tawk_API = window.Tawk_API || {};
        window.Tawk_LoadStart = new Date();
        var s1 = document.createElement("script");
        s1.async = true;
        s1.src = "https://embed.tawk.to/5e7d2de035bcbb0c9aaad04f/default";
        s1.charset = "UTF-8";
        s1.setAttribute("crossorigin", "*");
        document.body.appendChild(s1);
    }

    function apply(c) {
        if (c.embeds) loadEmbeds();
        if (c.chat) loadChat();
        /* Retirar el consentimiento tiene que surtir efecto: recargamos sin terceros */
        if ((!c.embeds && embedsLoaded) || (!c.chat && chatLoaded)) location.reload();
    }

    /* Aviso y panel de configuración */
    var banner = document.createElement("div");
    banner.className = "cookie-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-live", "polite");
    banner.setAttribute("aria-label", "Aviso de cookies");
    banner.innerHTML =
        '<div class="cookie-main">' +
            '<p class="cookie-title">Tu privacidad</p>' +
            '<p>Usamos almacenamiento técnico necesario para que la web funcione. Con tu permiso, también cargaremos contenido de terceros (mapas, vídeos, Instagram, formularios) y el chat de atención, que pueden instalar sus propias cookies. No usamos cookies de publicidad ni de analítica. <a href="' + COOKIES_URL + '">Política de cookies</a></p>' +
        '</div>' +
        '<div class="cookie-settings" hidden>' +
            '<label class="cookie-option"><input type="checkbox" checked disabled><span><strong>Necesarias</strong> Guardan tu elección sobre cookies. Siempre activas.</span></label>' +
            '<label class="cookie-option"><input type="checkbox" data-cat="embeds"><span><strong>Contenido externo</strong> Google Maps, Calendar y Forms, YouTube, Instagram, Typeform, SoundCloud, Cincopa y Evangeli.net.</span></label>' +
            '<label class="cookie-option"><input type="checkbox" data-cat="chat"><span><strong>Chat de atención</strong> Tawk.to, para hablar con la parroquia en directo.</span></label>' +
        '</div>' +
        '<div class="cookie-actions">' +
            '<button type="button" class="btn" data-act="reject">Rechazar</button>' +
            '<button type="button" class="btn" data-act="config">Configurar</button>' +
            '<button type="button" class="btn" data-act="save" hidden>Guardar selección</button>' +
            '<button type="button" class="btn" data-act="accept">Aceptar todas</button>' +
        '</div>';
    document.body.appendChild(banner);

    var settings = banner.querySelector(".cookie-settings");
    var boxEmbeds = banner.querySelector('[data-cat="embeds"]');
    var boxChat = banner.querySelector('[data-cat="chat"]');
    var btnConfig = banner.querySelector('[data-act="config"]');
    var btnSave = banner.querySelector('[data-act="save"]');

    function showBanner(openSettings) {
        var c = readConsent() || { embeds: false, chat: false };
        boxEmbeds.checked = c.embeds;
        boxChat.checked = c.chat;
        settings.hidden = !openSettings;
        btnSave.hidden = !openSettings;
        btnConfig.hidden = !!openSettings;
        banner.classList.add("open");
    }
    function hideBanner() { banner.classList.remove("open"); }

    banner.querySelector('[data-act="accept"]').addEventListener("click", function () { hideBanner(); apply(saveConsent(true, true)); });
    banner.querySelector('[data-act="reject"]').addEventListener("click", function () { hideBanner(); apply(saveConsent(false, false)); });
    btnConfig.addEventListener("click", function () { showBanner(true); });
    btnSave.addEventListener("click", function () { hideBanner(); apply(saveConsent(boxEmbeds.checked, boxChat.checked)); });
    document.querySelectorAll("[data-cookie-settings]").forEach(function (b) {
        b.addEventListener("click", function () { showBanner(true); });
    });

    var stored = readConsent();
    if (stored) apply(stored);
    else showBanner(false);
})();
