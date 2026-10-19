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

    /* --- Aviso de cookies --- */
    if (window.cookieconsent) {
        window.cookieconsent.initialise({
            palette: { popup: { background: "#111111", text: "#e8e2d6" }, button: { background: "#bfa065", text: "#ffffff" } },
            theme: "classic",
            position: "bottom-left",
            content: {
                message: "Utilizamos cookies para mejorar la calidad de nuestro servicio.",
                dismiss: "Aceptar",
                link: "Más información",
                href: COOKIES_URL
            }
        });
    }

    /* --- Chat Tawk.to --- */
    window.Tawk_API = window.Tawk_API || {};
    window.Tawk_LoadStart = new Date();
    var s1 = document.createElement("script");
    s1.async = true;
    s1.src = "https://embed.tawk.to/5e7d2de035bcbb0c9aaad04f/default";
    s1.charset = "UTF-8";
    s1.setAttribute("crossorigin", "*");
    document.body.appendChild(s1);
})();
