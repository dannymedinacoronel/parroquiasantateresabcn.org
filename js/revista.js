/* Revista digital: cada número se hojea como un libro (StPageFlip).
   El generador deja en la página los artículos como <template class="mag-src">; aquí se reparten
   en páginas del tamaño de la pantalla y se monta el libro. Si algo falla, debajo sigue la
   versión de texto con un enlace a cada artículo. */
(function () {
    var mag = document.querySelector("[data-mag]");
    if (!mag || !window.St || !St.PageFlip) return;
    var host = mag.querySelector(".mag-host");
    var counter = mag.querySelector(".mag-count");
    var btnPrev = mag.querySelector("[data-mag-prev]"), btnNext = mag.querySelector("[data-mag-next]");
    var btnIndex = mag.querySelector("[data-mag-index]"), btnFull = mag.querySelector("[data-mag-full]");
    var run = mag.getAttribute("data-run") || "";
    var lblPage = mag.getAttribute("data-label-page") || "Página";
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var pf = null, indexPage = 2, size = null;

    function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

    /* tamaño de página según el espacio disponible; el texto escala con la página */
    function measure() {
        var full = document.fullscreenElement === mag;
        var w = mag.clientWidth - 24, h = (full ? window.innerHeight - 110 : Math.max(window.innerHeight * 0.86, 520)) ;
        var portrait = w < 760;
        var pw = portrait ? Math.min(w, 520) : Math.min(520, Math.floor(w / 2));
        var ph = Math.round(pw * 1.414);
        if (ph > h) { ph = Math.round(h); pw = Math.round(ph / 1.414); }
        return { pw: Math.max(260, pw), ph: Math.max(368, ph), portrait: portrait };
    }

    function newPage(kind) {
        var pg = el("div", "mag-page " + (kind || ""));
        var inner = el("div", "mag-inner");
        pg.appendChild(inner);
        return { pg: pg, inner: inner };
    }
    function textPage(sz) {
        var p = newPage("mag-text");
        p.inner.appendChild(el("div", "mag-run", run));
        p.flow = el("div", "mag-flow");
        p.inner.appendChild(p.flow);
        p.folio = el("div", "mag-folio");
        p.inner.appendChild(p.folio);
        return p;
    }
    function overflows(flow) { return flow.scrollHeight > flow.clientHeight + 1; }

    /* reparte los bloques de un artículo en páginas; los párrafos largos se parten por palabras */
    function paginate(tpl, stage) {
        var blocks = Array.prototype.slice.call(tpl.content.children).map(function (n) { return n.cloneNode(true); });
        var pages = [], cur = textPage();
        stage.appendChild(cur.pg); pages.push(cur);
        function fresh() { cur = textPage(); stage.appendChild(cur.pg); pages.push(cur); }
        while (blocks.length) {
            var b = blocks.shift();
            cur.flow.appendChild(b);
            if (!overflows(cur.flow)) continue;
            cur.flow.removeChild(b);
            if (b.tagName === "P" && b.children.length === 0 && b.textContent.split(" ").length > 6) {
                var words = b.textContent.split(" "), lo = 0, hi = words.length, part = b.cloneNode(false);
                cur.flow.appendChild(part);
                while (lo < hi) {   // la mayor parte del párrafo que cabe en esta página
                    var mid = Math.ceil((lo + hi) / 2);
                    part.textContent = words.slice(0, mid).join(" ");
                    if (overflows(cur.flow)) hi = mid - 1; else lo = mid;
                }
                if (lo >= 3) {
                    part.textContent = words.slice(0, lo).join(" ");
                    var rest = b.cloneNode(false);
                    rest.classList.remove("illuminated");
                    rest.textContent = words.slice(lo).join(" ");
                    blocks.unshift(rest);
                    fresh();
                    continue;
                }
                cur.flow.removeChild(part);
            }
            if (cur.flow.children.length === 0) { cur.flow.appendChild(b); fresh(); continue; }   // no cabe ni sola: se recorta
            fresh();
            blocks.unshift(b);
        }
        if (!pages[pages.length - 1].flow.children.length) { stage.removeChild(cur.pg); pages.pop(); }
        return pages;
    }

    function build() {
        size = measure();
        host.innerHTML = "";
        mag.style.setProperty("--mag-pw", size.pw + "px");
        mag.style.setProperty("--mag-ph", size.ph + "px");
        // en el móvil (una sola página) la letra un poco más grande, para leer sin hacer zoom
        mag.style.setProperty("--mag-fs", (size.pw / (size.portrait ? 25 : 30)).toFixed(2) + "px");
        var stage = el("div", "mag-stage");
        host.appendChild(stage);

        var all = [];
        // portada y presentación (vienen ya maquetadas)
        mag.querySelectorAll("template.mag-fixed").forEach(function (t) {
            var p = newPage(t.getAttribute("data-kind"));
            p.inner.appendChild(t.content.cloneNode(true));
            if (t.getAttribute("data-kind") === "mag-cover") p.pg.setAttribute("data-density", "hard");
            stage.appendChild(p.pg);
            all.push(p);
        });
        // índice: se rellena cuando se sabe en qué página empieza cada artículo
        var idx = newPage("mag-index");
        idx.inner.appendChild(el("div", "mag-run", run));
        var idxBody = el("div", "mag-flow");
        idx.inner.appendChild(idxBody);
        idx.folio = el("div", "mag-folio");
        idx.inner.appendChild(idx.folio);
        stage.appendChild(idx.pg);
        all.push(idx);
        indexPage = all.length - 1;
        var entries = [];
        mag.querySelectorAll("template.mag-src").forEach(function (t) {
            var start = all.length;
            paginate(t, stage).forEach(function (p) { all.push(p); });
            entries.push({ n: start, sec: t.getAttribute("data-sec"), title: t.getAttribute("data-title"), author: t.getAttribute("data-author") });
        });
        // contraportada (página par: antes, una en blanco si hace falta)
        if (all.length % 2 === 0) { var blank = newPage("mag-blank"); stage.appendChild(blank.pg); all.push(blank); }
        var back = mag.querySelector("template.mag-back");
        if (back) { var bp = newPage("mag-backcover"); bp.pg.setAttribute("data-density", "hard"); bp.inner.appendChild(back.content.cloneNode(true)); stage.appendChild(bp.pg); all.push(bp); }

        idxBody.appendChild(el("h3", "mag-index-title", mag.getAttribute("data-label-index") || "En este número"));
        var list = el("ol", "mag-toc");
        entries.forEach(function (e) {
            var li = el("li");
            var a = el("button", "mag-toc-link");
            a.type = "button";
            a.innerHTML = (e.sec ? '<span class="mag-toc-sec">' + e.sec + "</span>" : "") + "<strong>" + e.title + "</strong>" +
                (e.author ? "<em>" + e.author + "</em>" : "") + '<span class="mag-toc-n">' + (e.n + 1) + "</span>";
            a.addEventListener("click", function () { if (pf) pf.flip(e.n); });
            li.appendChild(a);
            list.appendChild(li);
        });
        idxBody.appendChild(list);
        all.forEach(function (p, i) {
            p.pg.classList.add(i % 2 ? "mag-left" : "mag-right");
            if (p.folio) p.folio.textContent = String(i + 1);
        });

        // el libro
        var book = el("div", "mag-book");
        stage.parentNode.insertBefore(book, stage);
        all.forEach(function (p) { book.appendChild(p.pg); });
        stage.parentNode.removeChild(stage);
        host.style.width = (size.portrait ? size.pw : size.pw * 2) + "px";
        pf = new St.PageFlip(book, {
            width: size.pw, height: size.ph, size: "fixed", showCover: true, usePortrait: size.portrait,
            maxShadowOpacity: 0.45, flippingTime: reduce ? 1 : 900, mobileScrollSupport: true, autoSize: false, startZIndex: 1
        });
        pf.loadFromHTML(book.querySelectorAll(".mag-page"));
        pf.on("flip", update);
        update();
        mag.classList.add("ready");
    }

    function update() {
        if (!pf) return;
        var i = pf.getCurrentPageIndex(), n = pf.getPageCount();
        counter.textContent = lblPage + " " + (i + 1) + " / " + n;
        btnPrev.disabled = i <= 0;
        btnNext.disabled = i >= n - (size && size.portrait ? 1 : 2);
    }

    btnPrev.addEventListener("click", function () { if (pf) pf.flipPrev(); });
    btnNext.addEventListener("click", function () { if (pf) pf.flipNext(); });
    btnIndex.addEventListener("click", function () { if (pf) pf.flip(indexPage); });
    mag.addEventListener("keydown", function (e) {
        if (!pf) return;
        if (e.key === "ArrowRight") { pf.flipNext(); e.preventDefault(); }
        if (e.key === "ArrowLeft") { pf.flipPrev(); e.preventDefault(); }
    });
    if (btnFull) {
        if (!mag.requestFullscreen) btnFull.hidden = true;
        btnFull.addEventListener("click", function () {
            if (document.fullscreenElement) document.exitFullscreen(); else mag.requestFullscreen();
        });
        document.addEventListener("fullscreenchange", function () { rebuild(true); });
    }

    var timer = null, lastW = 0;
    function rebuild(force) {
        var keep = pf ? pf.getCurrentPageIndex() : 0;
        var next = measure();
        if (!force && size && Math.abs(next.pw - size.pw) < 24 && next.portrait === size.portrait) return;
        if (pf) { try { pf.destroy(); } catch (e) { } pf = null; }
        build();
        if (keep && pf) pf.turnToPage(Math.min(keep, pf.getPageCount() - 1));
        update();
    }
    window.addEventListener("resize", function () {
        if (window.innerWidth === lastW) return;   // en el móvil la barra del navegador cambia el alto: no rehacer
        lastW = window.innerWidth;
        clearTimeout(timer);
        timer = setTimeout(function () { rebuild(false); }, 350);
    });
    lastW = window.innerWidth;
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(build);
})();
