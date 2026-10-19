/* Parroquia Santa Teresa de Jesús — JavaScript común a todas las páginas */
(function () {
    /* --- Idioma de la página y textos del JavaScript en es / ca / en --- */
    var LANG = (document.documentElement.lang || "es").slice(0, 2);
    var I18N = {
        es: {
            menuOpen: "Abrir menú", menuClose: "Cerrar menú",
            massNow: "Eucaristía <strong>en curso</strong> · comenzó a las ", massNext: "Próxima eucaristía: ",
            today: "hoy", tomorrow: "mañana", at: " a las ", hours: " h",
            days: ["el domingo", "el lunes", "el martes", "el miércoles", "el jueves", "el viernes", "el sábado"],
            viewer: "Visor de fotos", close: "Cerrar", prev: "Anterior", next: "Siguiente",
            newsEmpty: "No se han podido cargar las noticias. Inténtalo más tarde.", readMore: "Leer en la web original", updated: "Actualizado:",
            srcVatican: "Vaticano", srcDiocese: "Arzobispado", featured: "Noticia destacada",
            external: "Contenido externo",
            phText: "Este contenido lo proporciona un servicio externo que puede instalar cookies. Solo se mostrará si lo aceptas.",
            phAccept: "Aceptar y mostrar", moreInfo: "Más información",
            bannerLabel: "Aviso de cookies", bannerTitle: "Tu privacidad",
            bannerText: "Usamos almacenamiento técnico necesario para que la web funcione. Con tu permiso, también cargaremos contenido de terceros (mapas, vídeos, Instagram, formularios) y el chat de atención, que pueden instalar sus propias cookies. No usamos cookies de publicidad ni de analítica.",
            policy: "Política de cookies",
            optNecessary: "<strong>Necesarias</strong> Guardan tu elección sobre cookies. Siempre activas.",
            optEmbeds: "<strong>Contenido externo</strong> Google Maps, Calendar y Forms, YouTube, Instagram, Typeform, SoundCloud, Cincopa, Evangeli.net y fotos de las noticias.",
            optChat: "<strong>Chat de atención</strong> Tawk.to, para hablar con la parroquia en directo.",
            reject: "Rechazar", configure: "Configurar", save: "Guardar selección", acceptAll: "Aceptar todas"
        },
        ca: {
            menuOpen: "Obrir menú", menuClose: "Tancar menú",
            massNow: "Eucaristia <strong>en curs</strong> · ha començat a les ", massNext: "Propera eucaristia: ",
            today: "avui", tomorrow: "demà", at: " a les ", hours: " h",
            days: ["diumenge", "dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte"],
            viewer: "Visor de fotos", close: "Tancar", prev: "Anterior", next: "Següent",
            newsEmpty: "No s'han pogut carregar les notícies. Torna-ho a provar més tard.", readMore: "Llegir al web original", updated: "Actualitzat:",
            srcVatican: "Vaticà", srcDiocese: "Arquebisbat", featured: "Notícia destacada",
            external: "Contingut extern",
            phText: "Aquest contingut el proporciona un servei extern que pot instal·lar galetes. Només es mostrarà si ho acceptes.",
            phAccept: "Acceptar i mostrar", moreInfo: "Més informació",
            bannerLabel: "Avís de galetes", bannerTitle: "La teva privacitat",
            bannerText: "Fem servir emmagatzematge tècnic necessari perquè el web funcioni. Amb el teu permís, també carregarem contingut de tercers (mapes, vídeos, Instagram, formularis) i el xat d'atenció, que poden instal·lar les seves pròpies galetes. No fem servir galetes de publicitat ni d'analítica.",
            policy: "Política de galetes",
            optNecessary: "<strong>Necessàries</strong> Desen la teva elecció sobre galetes. Sempre actives.",
            optEmbeds: "<strong>Contingut extern</strong> Google Maps, Calendar i Forms, YouTube, Instagram, Typeform, SoundCloud, Cincopa, Evangeli.net i fotos de les notícies.",
            optChat: "<strong>Xat d'atenció</strong> Tawk.to, per parlar amb la parròquia en directe.",
            reject: "Rebutjar", configure: "Configurar", save: "Desar la selecció", acceptAll: "Acceptar-les totes"
        },
        en: {
            menuOpen: "Open menu", menuClose: "Close menu",
            massNow: "Mass <strong>in progress</strong> · started at ", massNext: "Next Mass: ",
            today: "today", tomorrow: "tomorrow", at: " at ", hours: "",
            days: ["on Sunday", "on Monday", "on Tuesday", "on Wednesday", "on Thursday", "on Friday", "on Saturday"],
            viewer: "Photo viewer", close: "Close", prev: "Previous", next: "Next",
            newsEmpty: "The news could not be loaded. Please try again later.", readMore: "Read on the original website", updated: "Updated:",
            srcVatican: "Vatican", srcDiocese: "Archdiocese", featured: "Top story",
            external: "External content",
            phText: "This content is provided by an external service that may set cookies. It will only be shown if you accept.",
            phAccept: "Accept and show", moreInfo: "More information",
            bannerLabel: "Cookie notice", bannerTitle: "Your privacy",
            bannerText: "We use essential technical storage for the website to work. With your permission, we will also load third-party content (maps, videos, Instagram, forms) and the support chat, which may set their own cookies. We do not use advertising or analytics cookies.",
            policy: "Cookie policy",
            optNecessary: "<strong>Essential</strong> Store your cookie choice. Always active.",
            optEmbeds: "<strong>External content</strong> Google Maps, Calendar and Forms, YouTube, Instagram, Typeform, SoundCloud, Cincopa, Evangeli.net and news photos.",
            optChat: "<strong>Support chat</strong> Tawk.to, to talk to the parish live.",
            reject: "Reject", configure: "Settings", save: "Save selection", acceptAll: "Accept all"
        }
    };
    function T(key) { return (I18N[LANG] || I18N.es)[key]; }

    /* Ruta a la página de cookies del idioma actual, relativa a este script (que está en /js) */
    var SITE_ROOT = document.currentScript ? document.currentScript.src.replace(/js\/site\.js.*$/, "") : "";
    var COOKIES_URL = SITE_ROOT + (LANG === "es" ? "" : LANG + "/") + "html/cookies.html";

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
        hamburger.setAttribute("aria-label", open ? T("menuClose") : T("menuOpen"));
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
            if (window.innerWidth > 1280) setMenu(false);
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
                    texto = T("massNow") + horas[i];
                } else if (start > now) {
                    var cuando = off === 0 ? T("today") : off === 1 ? T("tomorrow") : T("days")[day.getDay()];
                    texto = T("massNext") + "<strong>" + cuando + T("at") + horas[i] + T("hours") + "</strong>";
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
        box.setAttribute("aria-label", T("viewer"));
        box.innerHTML = '<img alt=""><button class="lb-close" aria-label="' + T("close") + '">&times;</button>' +
            '<button class="lb-prev" aria-label="' + T("prev") + '">&#8249;</button><button class="lb-next" aria-label="' + T("next") + '">&#8250;</button>' +
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

    /* --- Noticias del Vaticano y del Arzobispado (data/noticias.js, actualizado a diario) --- */
    var NEWS_KEYS = {
        vaticano: { es: "vaticano_es", ca: "vaticano_es", en: "vaticano_en" },
        arzobispado: { es: "arzobispado_es", ca: "arzobispado_ca", en: "arzobispado_es" }
    };
    var LOCALE = { es: "es-ES", ca: "ca-ES", en: "en-GB" }[LANG] || "es-ES";
    function escapeHtml(s) {
        return String(s || "").replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }
    function fmtDate(iso, withTime) {
        var dt = new Date(iso);
        if (isNaN(dt)) return "";
        var opts = { day: "numeric", month: "long", year: "numeric" };
        if (withTime) { opts.hour = "2-digit"; opts.minute = "2-digit"; }
        return dt.toLocaleDateString(LOCALE, opts);
    }
    var data = window.NOTICIAS;
    var CROSS_SVG = '<svg viewBox="0 0 26 34" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round">' +
        '<path d="M13 1.5v31M4.5 10.5h17" stroke-width="2"/><circle cx="13" cy="10.5" r="3.4" stroke-width="1.3"/></svg>';
    var SOURCES = {
        vaticano: { badge: "vatican", label: T("srcVatican") },
        arzobispado: { badge: "diocese", label: T("srcDiocese") }
    };

    /* Imagen de la noticia: solo se pide al servidor externo si se aceptó el contenido externo.
       Mientras tanto (o si se rechaza) se ve un diseño con la cruz y el color de la fuente. */
    function newsMedia(n, src) {
        var img = "";
        if (n.imagen) {
            img = embedsLoaded
                ? '<img src="' + escapeHtml(n.imagen) + '" alt="" loading="lazy" onload="this.classList.add(\'ok\')" onerror="this.remove()">'
                : '<img data-consent-src="' + escapeHtml(n.imagen) + '" alt="" loading="lazy" onload="this.classList.add(\'ok\')" onerror="this.remove()">';
        }
        return '<div class="news-media ' + SOURCES[src].badge + '"><div class="news-ph">' + CROSS_SVG +
            "<span>" + SOURCES[src].label + "</span></div>" + img + "</div>";
    }
    function newsCard(n, featured) {
        var src = n.src;
        return '<a class="' + (featured ? "news-feature" : "news-card") + '" href="' + escapeHtml(n.enlace) + '" target="_blank" rel="noopener">' +
            newsMedia(n, src) +
            '<div class="news-body">' +
            '<div class="news-meta"><span class="news-badge ' + SOURCES[src].badge + '">' + SOURCES[src].label + "</span>" +
            '<time datetime="' + escapeHtml(n.fecha) + '">' + fmtDate(n.fecha) + "</time></div>" +
            (featured ? '<span class="news-kicker">' + T("featured") + "</span>" : "") +
            "<h3>" + escapeHtml(n.titulo) + "</h3>" +
            (n.resumen ? "<p>" + escapeHtml(n.resumen) + "</p>" : "") +
            '<span class="news-more">' + T("readMore") + " &rarr;</span></div></a>";
    }
    /* Noticias de ambas fuentes intercaladas (el Vaticano publica mucho más y, ordenando
       solo por fecha, las del Arzobispado quedarían siempre al final) */
    function allNews() {
        if (!data) return [];
        var bySource = Object.keys(NEWS_KEYS).map(function (src) {
            return (data[NEWS_KEYS[src][LANG]] || []).map(function (n) {
                var copy = {}; for (var k in n) copy[k] = n[k];
                copy.src = src;
                return copy;
            }).sort(function (a, b) { return new Date(b.fecha) - new Date(a.fecha); });
        });
        /* empieza la fuente con la noticia más reciente */
        bySource.sort(function (a, b) {
            return new Date((b[0] || {}).fecha || 0) - new Date((a[0] || {}).fecha || 0);
        });
        var list = [];
        for (var i = 0; i < Math.max(bySource[0].length, bySource[1].length); i++) {
            if (bySource[0][i]) list.push(bySource[0][i]);
            if (bySource[1][i]) list.push(bySource[1][i]);
        }
        return list;
    }
    document.querySelectorAll("[data-news-page]").forEach(function (board) {
        var items = allNews();
        function render(filter) {
            var list = items.filter(function (n) { return filter === "all" || n.src === filter; });
            if (!list.length) {
                board.innerHTML = '<p class="news-empty">' + T("newsEmpty") + "</p>";
                return;
            }
            board.innerHTML = newsCard(list[0], true) +
                '<div class="news-cards">' + list.slice(1).map(function (n) { return newsCard(n, false); }).join("") + "</div>";
        }
        render("all");
        document.querySelectorAll(".news-filters [data-filter]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                document.querySelectorAll(".news-filters [data-filter]").forEach(function (b) {
                    b.setAttribute("aria-pressed", b === btn ? "true" : "false");
                });
                render(btn.dataset.filter);
            });
        });
    });
    document.querySelectorAll("[data-news-updated]").forEach(function (el) {
        if (data && data.actualizado) el.textContent = T("updated") + " " + fmtDate(data.actualizado, true);
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
        document.querySelectorAll("iframe[data-consent-src], img[data-consent-src]").forEach(function (f) {
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
        ph.innerHTML = '<p><strong>' + (box.dataset.service || T("external")) + '</strong></p>' +
            '<p>' + T("phText") + '</p>' +
            '<button type="button" class="btn btn-solid">' + T("phAccept") + '</button> ' +
            '<a href="' + COOKIES_URL + '">' + T("moreInfo") + '</a>';
        ph.querySelector("button").addEventListener("click", function () {
            var c = readConsent() || {};
            apply(saveConsent(true, c.chat));
            hideBanner();
        });
        box.insertBefore(ph, box.firstChild);
    });

    /* Botones sueltos que aceptan el contenido externo (p. ej. "Mostrar fotos" en Noticias) */
    document.querySelectorAll("[data-consent-accept]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var c = readConsent() || {};
            apply(saveConsent(true, c.chat));
            hideBanner();
        });
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
        document.documentElement.classList.toggle("consent-embeds", !!c.embeds);
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
    banner.setAttribute("aria-label", T("bannerLabel"));
    banner.innerHTML =
        '<div class="cookie-main">' +
            '<p class="cookie-title">' + T("bannerTitle") + '</p>' +
            '<p>' + T("bannerText") + ' <a href="' + COOKIES_URL + '">' + T("policy") + '</a></p>' +
        '</div>' +
        '<div class="cookie-settings" hidden>' +
            '<label class="cookie-option"><input type="checkbox" checked disabled><span>' + T("optNecessary") + '</span></label>' +
            '<label class="cookie-option"><input type="checkbox" data-cat="embeds"><span>' + T("optEmbeds") + '</span></label>' +
            '<label class="cookie-option"><input type="checkbox" data-cat="chat"><span>' + T("optChat") + '</span></label>' +
        '</div>' +
        '<div class="cookie-actions">' +
            '<button type="button" class="btn" data-act="reject">' + T("reject") + '</button>' +
            '<button type="button" class="btn" data-act="config">' + T("configure") + '</button>' +
            '<button type="button" class="btn" data-act="save" hidden>' + T("save") + '</button>' +
            '<button type="button" class="btn" data-act="accept">' + T("acceptAll") + '</button>' +
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
