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
            todayBadge: "Hoy", backTop: "Volver arriba",
            external: "Contenido externo",
            formSending: "Enviando…", formOkContact: "¡Mensaje enviado! Gracias por escribirnos. Te responderemos lo antes posible.", formOk: "¡Inscripción recibida! Gracias. La parroquia se pondrá en contacto con vosotros muy pronto.",
            formErr: "No se ha podido enviar. Inténtalo de nuevo en unos minutos o llámanos al +34 619 040 913.",
            phText: "Este contenido lo proporciona un servicio externo que puede instalar cookies. Solo se mostrará si lo aceptas.",
            phAccept: "Aceptar y mostrar", moreInfo: "Más información",
            bannerLabel: "Aviso de cookies", bannerTitle: "Tu privacidad",
            bannerText: "Usamos almacenamiento técnico necesario para que la web funcione. Con tu permiso, también cargaremos contenido de terceros (mapas, vídeos, Instagram, formularios), que pueden instalar sus propias cookies. No usamos cookies de publicidad ni de analítica.",
            policy: "Política de cookies",
            optNecessary: "<strong>Necesarias</strong> Guardan tu elección sobre cookies. Siempre activas.",
            optEmbeds: "<strong>Contenido externo</strong> Google Maps, YouTube, Instagram, SoundCloud, Cincopa, Evangeli.net y fotos de las noticias.",
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
            todayBadge: "Avui", backTop: "Tornar a dalt",
            external: "Contingut extern",
            formSending: "S'està enviant…", formOkContact: "Missatge enviat! Gràcies per escriure'ns. Et respondrem al més aviat possible.", formOk: "Inscripció rebuda! Gràcies. La parròquia es posarà en contacte amb vosaltres molt aviat.",
            formErr: "No s'ha pogut enviar. Torna-ho a provar d'aquí a uns minuts o truca'ns al +34 619 040 913.",
            phText: "Aquest contingut el proporciona un servei extern que pot instal·lar galetes. Només es mostrarà si ho acceptes.",
            phAccept: "Acceptar i mostrar", moreInfo: "Més informació",
            bannerLabel: "Avís de galetes", bannerTitle: "La teva privacitat",
            bannerText: "Fem servir emmagatzematge tècnic necessari perquè el web funcioni. Amb el teu permís, també carregarem contingut de tercers (mapes, vídeos, Instagram, formularis), que poden instal·lar les seves pròpies galetes. No fem servir galetes de publicitat ni d'analítica.",
            policy: "Política de galetes",
            optNecessary: "<strong>Necessàries</strong> Desen la teva elecció sobre galetes. Sempre actives.",
            optEmbeds: "<strong>Contingut extern</strong> Google Maps, YouTube, Instagram, SoundCloud, Cincopa, Evangeli.net i fotos de les notícies.",
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
            todayBadge: "Today", backTop: "Back to top",
            external: "External content",
            formSending: "Sending…", formOkContact: "Message sent! Thank you for writing to us. We will reply as soon as possible.", formOk: "Registration received! Thank you. The parish will get in touch with you very soon.",
            formErr: "It could not be sent. Please try again in a few minutes or call us on +34 619 040 913.",
            phText: "This content is provided by an external service that may set cookies. It will only be shown if you accept.",
            phAccept: "Accept and show", moreInfo: "More information",
            bannerLabel: "Cookie notice", bannerTitle: "Your privacy",
            bannerText: "We use essential technical storage for the website to work. With your permission, we will also load third-party content (maps, videos, Instagram, forms), which may set their own cookies. We do not use advertising or analytics cookies.",
            policy: "Cookie policy",
            optNecessary: "<strong>Essential</strong> Store your cookie choice. Always active.",
            optEmbeds: "<strong>External content</strong> Google Maps, YouTube, Instagram, SoundCloud, Cincopa, Evangeli.net and news photos.",
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
        navMenu.querySelectorAll(".nav-link, .sub-link").forEach(function (link) {
            link.addEventListener("click", function () {
                setMenu(false);
                link.blur(); /* que el submenú no se quede abierto por el foco al volver atrás */
            });
        });

        /* Submenús: botón ⌄ (acordeón en móvil; también abre el panel con teclado en ordenador) */
        navMenu.querySelectorAll(".sub-toggle").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var item = btn.parentNode;
                var open = !item.classList.contains("open");
                navMenu.querySelectorAll(".nav-item.open").forEach(function (other) {
                    if (other !== item) {
                        other.classList.remove("open");
                        other.querySelector(".sub-toggle").setAttribute("aria-expanded", "false");
                    }
                });
                item.classList.toggle("open", open);
                btn.setAttribute("aria-expanded", open ? "true" : "false");
            });
        });
        document.addEventListener("click", function (e) {
            if (window.innerWidth > 1280 && !e.target.closest(".nav-item.has-sub")) {
                navMenu.querySelectorAll(".nav-item.open").forEach(function (item) {
                    item.classList.remove("open");
                    item.querySelector(".sub-toggle").setAttribute("aria-expanded", "false");
                });
            }
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
        ".icon-card", ".mosaic a", ".info-cards", ".org-node", ".cta-band", ".priest-card", ".book-page", ".reading-author", ".reading-audio", ".reading-nav", ".reflection-card", ".open-book", ".homily-chip"
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
    var MISAS = { 0: ["11:00", "13:15"], 1: ["19:00"], 2: ["19:00"], 3: ["19:00"], 4: ["19:00"], 5: ["19:00"], 6: ["19:00"] };
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
    var NEWS_PER_SOURCE = 3;  // solo las 3 más recientes del Vaticano y las 3 del Arzobispado
    function allNews() {
        if (!data) return [];
        var bySource = Object.keys(NEWS_KEYS).map(function (src) {
            return (data[NEWS_KEYS[src][LANG]] || []).map(function (n) {
                var copy = {}; for (var k in n) copy[k] = n[k];
                copy.src = src;
                return copy;
            }).sort(function (a, b) { return new Date(b.fecha) - new Date(a.fecha); }).slice(0, NEWS_PER_SOURCE);
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

    /* ======================================================================
       INTERACTIVIDAD
       ====================================================================== */
    var REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var FINE_POINTER = window.matchMedia && window.matchMedia("(any-hover: hover) and (pointer: fine)").matches;

    /* --- Cifras que cuentan hacia arriba al aparecer en pantalla --- */
    var counters = document.querySelectorAll("[data-count]");
    function runCounter(el) {
        var to = +el.dataset.count, from = +(el.dataset.from || 0), prefix = el.dataset.prefix || "";
        var start = null, dur = 1800 + Math.min(Math.abs(to - from), 200) * 3;
        function step(t) {
            if (!start) start = t;
            var p = Math.min((t - start) / dur, 1);
            var eased = 1 - Math.pow(1 - p, 4);
            el.textContent = prefix + Math.round(from + (to - from) * eased);
            if (p < 1) requestAnimationFrame(step);
            else el.classList.add("counted");
        }
        requestAnimationFrame(step);
    }
    if (counters.length && "IntersectionObserver" in window && !REDUCED) {
        var countIO = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) { runCounter(entry.target); countIO.unobserve(entry.target); }
            });
        }, { threshold: 0.6 });
        counters.forEach(function (el) {
            el.textContent = (el.dataset.prefix || "") + (el.dataset.from || 0);
            countIO.observe(el);
        });
    }

    /* --- Horario: resaltar el día de hoy --- */
    var todayIdx = new Date().getDay();
    document.querySelectorAll("[data-days]").forEach(function (el) {
        if (el.dataset.days.split(",").indexOf(String(todayIdx)) === -1) return;
        el.classList.add("is-today");
        var tag = document.createElement("span");
        tag.className = "today-tag";
        tag.textContent = T("todayBadge");
        el.insertBefore(tag, el.firstChild);
    });

    /* --- Barra de progreso de lectura y botón "volver arriba" --- */
    var progress = document.createElement("div");
    progress.className = "scroll-progress";
    progress.setAttribute("aria-hidden", "true");
    (header || document.body).appendChild(progress); /* en el borde inferior de la cabecera */
    var toTop = document.createElement("button");
    toTop.type = "button";
    toTop.className = "to-top";
    toTop.setAttribute("aria-label", T("backTop"));
    toTop.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
    toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: REDUCED ? "auto" : "smooth" }); });
    document.body.appendChild(toTop);

    /* --- Línea del tiempo que se dibuja al bajar --- */
    var timeline = document.querySelector(".timeline");

    var ticking = false;
    function onScrollFx() {
        ticking = false;
        var doc = document.documentElement;
        var max = doc.scrollHeight - window.innerHeight;
        var ratio = max > 0 ? window.scrollY / max : 0;
        progress.style.transform = "scaleX(" + ratio + ")";
        toTop.classList.toggle("show", window.scrollY > window.innerHeight * 0.8);
        if (timeline) {
            var r = timeline.getBoundingClientRect();
            var fill = (window.innerHeight * 0.65 - r.top) / r.height;
            timeline.style.setProperty("--fill", Math.max(0, Math.min(1, fill)));
        }
    }
    window.addEventListener("scroll", function () {
        if (!ticking) { ticking = true; requestAnimationFrame(onScrollFx); }
    }, { passive: true });
    onScrollFx();

    /* --- La cita de Santa Teresa aparece palabra a palabra --- */
    document.querySelectorAll(".quote blockquote").forEach(function (q) {
        if (REDUCED) return;
        var words = q.textContent.trim().split(/\s+/);
        q.innerHTML = words.map(function (w, i) {
            return '<span class="w" style="transition-delay:' + (i * 55) + 'ms">' + escapeHtml(w) + "</span>";
        }).join(" ");
        q.classList.add("words");
    });

    /* --- Tarjetas que se inclinan siguiendo el ratón (solo ordenador) --- */
    if (FINE_POINTER && !REDUCED) {
        document.querySelectorAll(".feature, .icon-card, .news-card, .news-feature, .info-card, .org-node").forEach(function (card) {
            card.classList.add("tilt");
            var rect = null;   // se mide una vez al entrar, no en cada movimiento del ratón
            card.addEventListener("pointerenter", function () { rect = card.getBoundingClientRect(); });
            card.addEventListener("pointermove", function (e) {
                var r = rect || (rect = card.getBoundingClientRect());
                var x = (e.clientX - r.left) / r.width - 0.5;
                var y = (e.clientY - r.top) / r.height - 0.5;
                card.style.transitionDelay = "0ms"; /* sin el retardo de la animación de entrada */
                card.style.transform = "perspective(900px) rotateX(" + (-y * 6) + "deg) rotateY(" + (x * 6) + "deg) translateY(-4px)";
                card.style.setProperty("--mx", (x + 0.5) * 100 + "%");
                card.style.setProperty("--my", (y + 0.5) * 100 + "%");
            });
            card.addEventListener("pointerleave", function () { card.style.transform = ""; rect = null; });
        });
    }

    /* --- Fechas de las reflexiones en el idioma de la página --- */
    /* --- Etiqueta «Nueva» en la reflexión de los últimos 30 días --- */
    function daysSince(iso) {
        var p = (iso || "").split("-");
        if (p.length < 3) return Infinity;
        var now = new Date();
        return (Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) - Date.UTC(+p[0], +p[1] - 1, +p[2])) / 864e5;
    }
    var NEW_DAYS = 30;
    document.querySelectorAll(".new-badge[data-new]").forEach(function (b) {
        var d = daysSince(b.getAttribute("data-new"));
        if (d >= 0 && d <= NEW_DAYS) b.hidden = false;
    });

    function localizeDates(root) {
      root.querySelectorAll("time[data-fmt]").forEach(function (t) {
        var p = (t.getAttribute("datetime") || "").split("-");
        if (p.length < 3) return;
        var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
        if (isNaN(d)) return;
        if (t.dataset.fmt === "long") {
            t.textContent = d.toLocaleDateString(LOCALE, { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
        } else if (t.dataset.fmt === "badge") {
            var m = t.querySelector(".db-m");
            if (m) m.textContent = d.toLocaleDateString(LOCALE, { month: "short", timeZone: "UTC" }).replace(".", "");
        }
      });
    }
    localizeDates(document);

    /* --- Archivo de reflexiones: filtro por autor --- */
    document.querySelectorAll(".rf-filters [data-author]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var who = btn.dataset.author;
            document.querySelectorAll(".rf-filters [data-author]").forEach(function (b) {
                b.setAttribute("aria-pressed", b === btn ? "true" : "false");
            });
            document.querySelectorAll(".rf-row").forEach(function (row) {
                row.hidden = !!who && row.dataset.author !== who;
            });
            document.querySelectorAll(".rf-year").forEach(function (y) {
                var n = y.nextElementSibling, any = false;
                while (n && !n.classList.contains("rf-year")) { if (!n.hidden) any = true; n = n.nextElementSibling; }
                y.hidden = !any;
            });
        });
    });

    /* --- Fotos de fondo que están lejos: se descargan cuando el visitante se acerca --- */
    (function () {
        var lazy = document.querySelectorAll("[data-bg]");
        function show(el) { el.style.backgroundImage = "url('" + new URL(el.getAttribute("data-bg"), location.href).href + "')"; el.removeAttribute("data-bg"); }
        if (!("IntersectionObserver" in window)) { lazy.forEach(show); return; }
        var io = new IntersectionObserver(function (es) {
            es.forEach(function (e) { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } });
        }, { rootMargin: "800px 0px" });
        lazy.forEach(function (el) { io.observe(el); });
    })();

    /* --- Visitas anónimas (dashboard → pestaña «Visitas») ---
       Se cuenta la página vista, el idioma, el tipo de pantalla y la web de procedencia; mientras
       la pestaña está a la vista se avisa cada 30 s para saber cuántas personas hay ahora mismo.
       Sin cookies, sin guardar nada en el navegador y sin IP. No cuenta el panel ni los robots,
       ni las páginas que el navegador prepara por adelantado hasta que de verdad se abren. */
    (function () {
        if (location.protocol !== "https:" || /^\/admin/.test(location.pathname) || navigator.webdriver) return;
        function send(data) {
            var body = JSON.stringify(data);
            try { if (navigator.sendBeacon && navigator.sendBeacon("/api/hit", new Blob([body], { type: "text/plain" }))) return; } catch (err) { }
            fetch("/api/hit", { method: "POST", body: body, keepalive: true }).catch(function () { });
        }
        function start() {
            var ref = "", entry = true;
            try {
                var r = document.referrer ? new URL(document.referrer) : null;
                if (r && r.host === location.host) entry = false; else if (r) ref = r.hostname;
            } catch (err) { }
            var w = window.innerWidth;
            send({ k: "view", p: location.pathname.replace(/^\/(ca|en)(?=\/|$)/, "") || "/", l: LANG, d: w < 700 ? "movil" : w < 1100 ? "tablet" : "ordenador", r: ref, e: entry ? 1 : 0 });
            var beats = 0, timer = setInterval(function () {
                if (document.visibilityState !== "visible") return;
                if (++beats > 60) return clearInterval(timer);     // como mucho 30 min por página
                send({ k: "ping" });
            }, 30000);
        }
        if (document.prerendering) document.addEventListener("prerenderingchange", start, { once: true });
        else start();
    })();

    /* --- Formularios que se envían por correo (FormSubmit → albertsols@gmail.com) ---
       Sin JavaScript el formulario se envía igualmente con su «action»; con JavaScript se envía
       sin salir de la página y se muestra la confirmación. */
    /* Métricas anónimas de los formularios (panel /admin/metricas.html): solo se cuenta que el
       formulario se ha visto, empezado, enviado o ha fallado, y su motivo. Sin cookies ni datos personales. */
    function trackForm(form, type) {
        if (location.protocol !== "https:" && location.hostname !== "localhost") return;   // no desde archivos sueltos
        var pf = form.querySelector("[data-purpose]");
        var picked = pf && (pf.value != null ? { value: pf.value } : pf.querySelector("input:checked"));   // desplegable o botones
        var payload = JSON.stringify({ form: form.getAttribute("data-form-id"), type: type, purpose: picked ? picked.value : "", lang: LANG });
        try {
            if (navigator.sendBeacon && navigator.sendBeacon("/api/form-event", new Blob([payload], { type: "text/plain" }))) return;
        } catch (err) { }
        fetch("/api/form-event", { method: "POST", body: payload, keepalive: true }).catch(function () { });
    }
    document.querySelectorAll("form[data-mail-form]").forEach(function (form) {
        var status = form.querySelector(".form-status");
        /* Botones de motivo: la ayuda del mensaje cambia según lo elegido y algunos motivos muestran
           un aviso (p. ej. Primera Comunión tiene su propio formulario). Si se llega desde otra página
           con ?motivo=Bautizo, ese botón ya aparece marcado y el cursor espera en el primer campo vacío. */
        var area = form.querySelector("textarea");
        var baseHint = area ? area.getAttribute("placeholder") : "";
        function onPick() {
            var c = form.querySelector(".motive-picker input:checked");
            if (area && c && c.name === "Motivo") area.setAttribute("placeholder", c.getAttribute("data-hint") || baseHint);
            form.querySelectorAll(".motive-note").forEach(function (n) { n.hidden = !(c && n.getAttribute("data-for") === c.value); });
        }
        form.addEventListener("change", function (e) { if (e.target.closest(".motive-picker")) onPick(); });
        var want = new URLSearchParams(location.search).get("motivo");
        if (want) {
            var chip = Array.prototype.find.call(form.querySelectorAll(".motive-picker input"), function (i) { return i.value === want; });
            if (chip) {
                chip.checked = true;
                chip.closest(".chip").classList.add("preset");
                onPick();
                var first = Array.prototype.find.call(form.querySelectorAll("input[type=text]:not(.hp-field), input[type=email], input[type=tel], textarea"), function (i) { return !i.value; });
                if (first && window.matchMedia("(min-width: 900px)").matches) setTimeout(function () { first.focus({ preventScroll: true }); }, 600);
            }
        }
        /* visto (una vez, cuando al menos un tercio entra en pantalla) y empezado (primer campo tocado) */
        if ("IntersectionObserver" in window) {
            var seenObs = new IntersectionObserver(function (es) {
                if (es[0].isIntersecting) { trackForm(form, "view"); seenObs.disconnect(); }
            }, { threshold: 0.33 });
            seenObs.observe(form);
        }
        form.addEventListener("input", function once() { trackForm(form, "start"); form.removeEventListener("input", once); });
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            var btn = form.querySelector("button[type=submit]");
            var data = {};
            new FormData(form).forEach(function (v, k) { data[k] = v; });
            if (data._honey) return;                        // casilla trampa para robots
            var mail = form.querySelector("input[type=email]");
            if (mail && mail.value) data._replyto = mail.value; // responder directamente a quien escribe
            /* El correo empieza con un saludo escrito con los datos del formulario («Hola, soy Ana…») y
               el asunto dice quién escribe y para qué. En las plantillas, {Campo} es el valor de ese campo
               y lo que va entre [ ] solo aparece si sus campos están rellenos. */
            function fill(tpl) {
                return tpl.replace(/\[([^\]]*)\]/g, function (m, part) {
                    var empty = false;
                    part.replace(/\{([^}]+)\}/g, function (x, k) { if (!String(data[k] || "").trim()) empty = true; });
                    return empty ? "" : part;
                }).replace(/\{([^}]+)\}/g, function (x, k) { return String(data[k] || "").trim(); }).replace(/\s+/g, " ").trim();
            }
            if (form.getAttribute("data-subject")) data._subject = fill(form.getAttribute("data-subject"));
            if (form.getAttribute("data-intro")) {
                var ordered = { "Resumen": fill(form.getAttribute("data-intro")) };
                Object.keys(data).forEach(function (k) {
                    var v = String(data[k]).trim();
                    if (k === "Formulario" || (!v && k.charAt(0) !== "_")) return;   // sin filas vacías
                    var d = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
                    ordered[k] = d ? d[3] + "/" + d[2] + "/" + d[1] : data[k];          // fechas como 04/05/2018
                });
                data = ordered;
            }
            btn.disabled = true;
            status.className = "form-status";
            status.textContent = T("formSending");
            fetch(form.getAttribute("data-mail-form"), {
                method: "POST",
                headers: { "Content-Type": "application/json", "Accept": "application/json" },
                body: JSON.stringify(data)
            }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return r.ok && String(j.success) !== "false"; }); })
              .then(function (ok) {
                  if (!ok) throw new Error("envío");
                  trackForm(form, "submit");
                  form.classList.add("sent");
                  status.className = "form-status ok";
                  status.textContent = T(form.getAttribute("data-ok") || "formOk");
                  form.reset();
                  status.scrollIntoView({ behavior: "smooth", block: "center" });
              })
              .catch(function () {
                  trackForm(form, "error");
                  status.className = "form-status err";
                  status.textContent = T("formErr");
                  btn.disabled = false;
              });
        });
    });

    /* --- Portada: pase de fotos ---
       La primera foto entra con el zoom de siempre; luego cada 7 s otra foto entra con un
       fundido y su propio movimiento. Cada foto se descarga antes de su turno y el pase se
       detiene si la portada no se ve o la pestaña está en segundo plano. */
    (function () {
        var box = document.querySelector(".hero-slides");
        if (!box) return;
        var slides = box.querySelectorAll(".hero-slide");
        if (slides.length < 2) return;
        var dots = document.querySelectorAll(".hero-dots i");
        var cap = document.querySelector("[data-hero-caption]");
        var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var SLIDE = 7000, FIRST = 9500;
        var cur = 0, timer = null, waiting = false, visible = true, loaded = [true];

        slides[0].classList.add("intro");
        function preload(i) {
            var s = slides[i];
            if (!s || s.classList.contains("ready")) return;
            s.classList.add("ready");
            var m = /url\(["']?(.*?)["']?\)/.exec(getComputedStyle(s).backgroundImage || "");
            if (!m) { loaded[i] = true; return; }
            var im = new Image();
            im.onload = im.onerror = function () { loaded[i] = true; };
            im.src = m[1];
        }
        function caption(i) {
            if (!cap) return;
            var txt = (slides[i].textContent || "").trim();
            if (!cap.textContent) { cap.textContent = txt; return; }
            cap.classList.add("fade");
            setTimeout(function () { cap.textContent = txt; cap.classList.remove("fade"); }, 600);
        }
        function setDots(i, ms) {
            dots.forEach(function (d, k) { d.classList.remove("on"); d.classList.toggle("done", k < i); });
            if (!dots[i]) return;
            dots[i].style.setProperty("--slide-ms", ms + "ms");
            void dots[i].offsetWidth; // reinicia la barra
            dots[i].classList.add("on");
        }
        function schedule(ms) {
            clearTimeout(timer);
            timer = setTimeout(next, ms);
        }
        function next() {
            var n = (cur + 1) % slides.length;
            if (!visible || document.hidden) { waiting = true; return; }
            if (!loaded[n]) { preload(n); timer = setTimeout(next, 400); return; }
            var prev = slides[cur], el = slides[n];
            prev.classList.remove("is-on");
            prev.classList.add("was-on");
            el.classList.remove("was-on", "intro");
            el.classList.add("is-on");
            setTimeout(function () { prev.classList.remove("was-on", "intro"); }, 2200);
            cur = n;
            caption(n);
            setDots(n, SLIDE);
            preload((n + 1) % slides.length);
            schedule(SLIDE);
        }
        function resume() {
            if (waiting && visible && !document.hidden) { waiting = false; next(); }
        }

        caption(0);
        /* La entrada con zoom empieza cuando la primera foto ya está descargada (antes arrancaba
           sobre el fondo vacío y parecía que se quedaba parada). Como mucho se espera 2,5 s. */
        var started = false;
        function start() {
            if (started) return;
            started = true;
            box.classList.add("loaded");
            if (reduce) { var ui = document.querySelector(".hero-slider-ui"); if (ui) ui.hidden = true; return; }
            setDots(0, FIRST);
            setTimeout(function () { preload(1); }, 2500);
            schedule(FIRST);
        }
        var m0 = /url\(["']?(.*?)["']?\)/.exec(getComputedStyle(slides[0]).backgroundImage || "");
        if (m0) {
            var im0 = new Image();
            im0.onload = im0.onerror = start;
            im0.src = m0[1];
            if (im0.complete) start();
        } else start();
        setTimeout(start, 2500);
        if (reduce) return;
        document.addEventListener("visibilitychange", resume);
        if ("IntersectionObserver" in window) {
            new IntersectionObserver(function (es) { visible = es[0].isIntersecting; resume(); }).observe(box);
        }
    })();

    /* --- Cambio de idioma sin perder el sitio ---
       Las otras versiones de idioma se preparan en segundo plano (speculationrules en el <head>),
       así que el cambio es instantáneo; aquí se recuerda hasta dónde se había bajado. */
    var SCROLL_KEY = "pst-langscroll";
    document.addEventListener("click", function (e) {
        var a = e.target.closest && e.target.closest("a[hreflang]");
        if (!a || e.ctrlKey || e.metaKey || e.shiftKey) return;
        var max = document.documentElement.scrollHeight - window.innerHeight;
        try {
            sessionStorage.setItem(SCROLL_KEY, JSON.stringify({ to: a.href.split("#")[0], ratio: max > 0 ? window.scrollY / max : 0 }));
        } catch (err) { }
    });
    function restoreLangScroll() {
        var s = null;
        try { s = JSON.parse(sessionStorage.getItem(SCROLL_KEY) || "null"); } catch (err) { }
        if (!s || s.to !== location.href.split("#")[0]) return;
        try { sessionStorage.removeItem(SCROLL_KEY); } catch (err) { }
        var max = document.documentElement.scrollHeight - window.innerHeight;
        if (s.ratio > 0 && max > 0) window.scrollTo({ top: Math.round(s.ratio * max), behavior: "instant" });
    }
    restoreLangScroll();
    /* página preparada en segundo plano: se coloca justo antes de mostrarse */
    window.addEventListener("pagereveal", restoreLangScroll);

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


    function apply(c) {
        document.documentElement.classList.toggle("consent-embeds", !!c.embeds);
        if (c.embeds) loadEmbeds();
        /* Retirar el consentimiento tiene que surtir efecto: recargamos sin terceros */
        if ((!c.embeds && embedsLoaded)) location.reload();
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

    var btnConfig = banner.querySelector('[data-act="config"]');
    var btnSave = banner.querySelector('[data-act="save"]');

    function showBanner(openSettings) {
        var c = readConsent() || { embeds: false, chat: false };
        boxEmbeds.checked = c.embeds;
        settings.hidden = !openSettings;
        btnSave.hidden = !openSettings;
        btnConfig.hidden = !!openSettings;
        banner.classList.add("open");
    }
    function hideBanner() { banner.classList.remove("open"); }

    banner.querySelector('[data-act="accept"]').addEventListener("click", function () { hideBanner(); apply(saveConsent(true, true)); });
    banner.querySelector('[data-act="reject"]').addEventListener("click", function () { hideBanner(); apply(saveConsent(false, false)); });
    btnConfig.addEventListener("click", function () { showBanner(true); });
    btnSave.addEventListener("click", function () { hideBanner(); apply(saveConsent(boxEmbeds.checked, false)); });
    document.querySelectorAll("[data-cookie-settings]").forEach(function (b) {
        b.addEventListener("click", function () { showBanner(true); });
    });

    var stored = readConsent();
    if (stored) apply(stored);
    else showBanner(false);

    /* ======================================================================
       AVISOS DE LA PARROQUIA (data/avisos.js)
       Tarjeta que aparece al entrar con la novedad del momento. Cada aviso se
       muestra una sola vez por visitante y espera a que se cierre el aviso de cookies.
       ====================================================================== */
    (function () {
        var list = window.AVISOS || [];
        var today = new Date().toISOString().slice(0, 10);
        function seen(id) { try { return localStorage.getItem("pst-aviso-" + id) === "1"; } catch (e) { return false; } }
        function markSeen(id) { try { localStorage.setItem("pst-aviso-" + id, "1"); } catch (e) { } }
        function txt(obj) { return obj ? (obj[LANG] || obj.es || "") : ""; }
        var aviso = null;
        for (var i = 0; i < list.length; i++) {
            var a = list[i];
            if (!a || !a.id || seen(a.id)) continue;
            if (a.desde && today < a.desde) continue;
            if (a.hasta && today > a.hasta) continue;
            aviso = a; break;
        }

        var card = document.createElement("aside");
        card.className = "notice-card";
        card.setAttribute("role", "dialog");
        card.setAttribute("aria-live", "polite");
        var closeBtn = '<button type="button" class="notice-close" aria-label="' + T("close") + '">&times;</button>';

        if (aviso) {
            /* Aviso escrito a mano en data/avisos.js (tiene prioridad) */
            var target = (aviso.enlace || "").replace(/^\/+/, "");
            /* no repetir el aviso en la propia página a la que enlaza */
            if (target && location.pathname.replace(/\.html$/, "").slice(-target.replace(/\.html$/, "").length) === target.replace(/\.html$/, "")) {
                markSeen(aviso.id);
                return;
            }
            var base = SITE_ROOT + (LANG === "es" ? "" : LANG + "/");
            card.setAttribute("aria-label", txt(aviso.titulo));
            card.innerHTML = closeBtn +
                (aviso.imagen ? '<div class="notice-photo"><img src="' + escapeHtml(SITE_ROOT + aviso.imagen) + '" alt=""></div>' : "") +
                '<div class="notice-body">' +
                    '<span class="notice-tag"><span class="notice-dot" aria-hidden="true"></span>' + escapeHtml(txt(aviso.etiqueta)) + "</span>" +
                    "<h3>" + escapeHtml(txt(aviso.titulo)) + "</h3>" +
                    "<p>" + escapeHtml(txt(aviso.texto)) + "</p>" +
                    (aviso.enlace ? '<a class="btn btn-solid notice-go" href="' + escapeHtml(base + target) + '">' + escapeHtml(txt(aviso.boton)) + " &rarr;</a>" : "") +
                "</div>";
        } else {
            /* Aviso automático: la última reflexión publicada (lo genera la web en cada página).
               Cada visitante lo ve una vez por reflexión; al publicar otra, vuelve a salir. */
            var tpl = document.getElementById("pst-ultima");
            if (!tpl) return;
            var id = tpl.getAttribute("data-id");
            if (seen(id)) return;
            /* quien ya está leyendo esa reflexión no necesita el aviso */
            if (location.pathname.indexOf("/" + tpl.getAttribute("data-slug") + ".html") > -1) { markSeen(id); return; }
            var fresh = daysSince(tpl.getAttribute("data-fecha")) <= NEW_DAYS;
            card.classList.add("notice-reflection");
            card.innerHTML = closeBtn;
            card.appendChild(tpl.content.cloneNode(true));
            card.querySelectorAll("[data-when]").forEach(function (s) { s.hidden = s.getAttribute("data-when") !== (fresh ? "new" : "old"); });
            localizeDates(card);
            var h3 = card.querySelector("h3");
            card.setAttribute("aria-label", h3 ? h3.textContent : "");
            aviso = { id: id };
        }
        document.body.appendChild(card);

        function close() {
            markSeen(aviso.id);
            card.classList.remove("open");
            setTimeout(function () { card.remove(); }, 600);
        }
        card.querySelector(".notice-close").addEventListener("click", close);
        var go = card.querySelector(".notice-go");
        if (go) go.addEventListener("click", function () { markSeen(aviso.id); });
        document.addEventListener("keydown", function (e) { if (e.key === "Escape" && card.classList.contains("open")) close(); });

        /* espera a que el aviso de cookies esté cerrado */
        function tryShow() {
            if (banner.classList.contains("open")) { setTimeout(tryShow, 800); return; }
            card.classList.add("open");
        }
        /* si la página se ha preparado en segundo plano, espera a que de verdad se vea */
        if (document.prerendering) document.addEventListener("prerenderingchange", function () { setTimeout(tryShow, 1600); }, { once: true });
        else setTimeout(tryShow, 1600);
    })();
})();
