// Editor visual de páginas (/admin/editor/). Usa la misma sesión que el panel (DecapBridge): la llave que el
// panel guarda al iniciar sesión (localStorage «pst-gw-token»), igual que el tablero de tareas (admin/dashboard.html).
// Guardar borrador -> contenido/paginas/_borradores/<página>.json (no publica la web)
// Publicar         -> contenido/paginas/<página>.json (Netlify vuelve a generar la web en 1-2 minutos)
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Puck } from "@puckeditor/core";
import "@puckeditor/core/puck.css";
import { makeRenderer, makeFilters, esc } from "./tpl.js";
import { TEMPLATES, makeConfig } from "./bloques.jsx";

const PAGE = new URLSearchParams(location.search).get("pagina") || "portada";
const MAIN = `contenido/paginas/${PAGE}.json`;
const DRAFT = `contenido/paginas/_borradores/${PAGE}.json`;
const ICON_NAMES = {
    agua: "Agua (bautismo)", paloma: "Paloma", anillos: "Anillos", manos: "Manos", oleo: "Óleo", caliz: "Cáliz", libro: "Libro",
    persona: "Persona", grupo: "Grupo", cal: "Calendario", nota: "Música", escoba: "Escoba", torre: "Campanario", globo: "Mundo",
    foto: "Foto", pin: "Ubicación", mail: "Correo", phone: "Teléfono", reloj: "Reloj", insta: "Instagram", cuentas: "Cuentas",
    barrio: "Barrio", tienda: "Tienda", monte: "Monte",
};

// ---------------------------------------------------------------- acceso a GitHub a través de DecapBridge
const gw = { url: null, repo: null, branch: "main", raw: null };
const ready = fetch("/admin/config.yml", { cache: "no-store" }).then((r) => r.text()).then((y) => {
    const g = /gateway_url:\s*(\S+)/.exec(y), rp = /\brepo:\s*(\S+)/.exec(y), br = /\bbranch:\s*(\S+)/.exec(y);
    gw.url = g ? g[1].replace(/\/+$/, "") + "/github" : null;
    gw.repo = rp && rp[1];
    if (br) gw.branch = br[1];
    gw.raw = `https://raw.githubusercontent.com/${gw.repo}/${gw.branch}/`;
});
function token() {
    try { const k = JSON.parse(localStorage.getItem("pst-gw-token") || "null"); if (k && k.t) return k.t; } catch (e) { /* sin llave */ }
    return "";
}
function who() {
    try { const u = JSON.parse(localStorage.getItem("decap-cms-user") || "null"); return (u && (u.name || u.email)) || "el equipo"; } catch (e) { return "el equipo"; }
}
const b64enc = (s) => btoa(unescape(encodeURIComponent(s)));
const b64dec = (s) => decodeURIComponent(escape(atob(s.replace(/\s/g, ""))));
async function api(path, opts = {}) {
    await ready;
    opts.headers = Object.assign({ Authorization: "Bearer " + token(), "Content-Type": "application/json" }, opts.headers || {});
    const r = await fetch(gw.url + "/repos/" + gw.repo + path, opts);
    if (r.status === 401 || r.status === 403) throw new Error("sesion");
    return r;
}
async function getFile(path) {
    const r = await api(`/contents/${path}?ref=${gw.branch}&t=${Date.now()}`);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error("HTTP " + r.status);
    const j = await r.json();
    return { sha: j.sha, text: b64dec(j.content) };
}
async function putFile(path, content64, message, sha) {
    const body = { message, branch: gw.branch, content: content64 };
    if (sha) body.sha = sha;
    const r = await api(`/contents/${path}`, { method: "PUT", body: JSON.stringify(body) });
    if (!r.ok) throw new Error(r.status === 409 || r.status === 422 ? "conflicto" : "HTTP " + r.status);
    return (await r.json()).content.sha;
}
async function deleteFile(path, sha, message) {
    const r = await api(`/contents/${path}`, { method: "DELETE", body: JSON.stringify({ message, sha, branch: gw.branch }) });
    if (!r.ok && r.status !== 404) throw new Error("HTTP " + r.status);
}

// ---------------------------------------------------------------- fotos
const uploaded = new Map();   // fotos subidas en esta sesión: ruta -> vista previa local
function imgUrl(v) {
    v = String(v || "").trim();
    if (!v) return "";
    if (uploaded.has(v)) return uploaded.get(v);
    if (/^(https?:)?\/\/|^\/|^data:|^blob:/.test(v)) return esc(v);
    // las fotos subidas desde el editor aún no están en la web hasta publicar: se ven desde GitHub
    if (v.startsWith("paginas/") && gw.raw) return esc(gw.raw + "fotosdefinitivas/web/" + v);
    return esc("/fotosdefinitivas/web/" + v);
}
function resize(file, max = 1600) {
    return new Promise((resolve, reject) => {
        const im = new Image();
        im.onload = () => {
            const k = Math.min(1, max / Math.max(im.width, im.height));
            const c = document.createElement("canvas");
            c.width = Math.round(im.width * k); c.height = Math.round(im.height * k);
            c.getContext("2d").drawImage(im, 0, 0, c.width, c.height);
            c.toBlob((b) => (b ? resolve(b) : reject(new Error("foto"))), "image/jpeg", 0.82);
        };
        im.onerror = () => reject(new Error("foto"));
        im.src = URL.createObjectURL(file);
    });
}
const slug = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\.[a-z0-9]+$/, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "foto";

function ImageField({ label, value, onChange }) {
    const [busy, setBusy] = useState(false);
    const input = useRef(null);
    async function pick(e) {
        const f = e.target.files && e.target.files[0];
        e.target.value = "";
        if (!f) return;
        setBusy(true);
        try {
            const blob = await resize(f);
            const b64 = await new Promise((res) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1]); r.readAsDataURL(blob); });
            const d = new Date().toISOString().slice(0, 10).replace(/-/g, "");
            const path = `paginas/${d}-${slug(f.name)}-${Math.random().toString(36).slice(2, 6)}.jpg`;
            await putFile("fotosdefinitivas/web/" + path, b64, `Foto subida desde el editor visual «${path}» — por ${who()}`);
            uploaded.set(path, URL.createObjectURL(blob));
            onChange(path);
        } catch (err) {
            alert(err.message === "sesion" ? "La sesión ha caducado. Vuelve a entrar en el panel y repite." : "No se ha podido subir la foto. Inténtalo de nuevo.");
        }
        setBusy(false);
    }
    const src = imgUrl(value).replace(/&amp;/g, "&");
    return (
        <div className="pst-img-field">
            <span className="pst-label">{label}</span>
            {src ? <img src={src} alt="" /> : <div className="pst-img-empty">Sin foto</div>}
            <div className="pst-img-actions">
                <button type="button" onClick={() => input.current.click()} disabled={busy}>{busy ? "Subiendo…" : "Subir una foto"}</button>
                <input ref={input} type="file" accept="image/*" hidden onChange={pick} />
            </div>
            <input className="pst-img-path" type="text" value={value || ""} onChange={(e) => onChange(e.target.value)} placeholder="o el nombre de una foto de la web" />
            <small className="pst-help">Si salen personas reconocibles, asegúrate de tener su permiso. No publiques caras de niños sin el permiso de sus padres.</small>
        </div>
    );
}

// ---------------------------------------------------------------- vista previa de los bloques automáticos
let livePage = null;
function liveSection(type) {
    const sel = { Horario: "#horarios", Reflexion: "#reflexion", Agenda: "#agenda", Actualidad: "#actualidad", Revista: "#revista", Ubicacion: "#ubicacion" }[type];
    if (!livePage) {
        livePage = fetch("/?vista-editor=" + Date.now()).then((r) => r.text()).then((h) => new DOMParser().parseFromString(h, "text/html")).catch(() => null);
    }
    return livePage.then((doc) => {
        const el = doc && doc.querySelector(sel);
        if (!el) return "";
        return el.outerHTML.replace(/(src|href|data-bg)="(?!https?:|\/|#|data:|mailto:|tel:)/g, '$1="/').replace(/url\('(?!https?:|\/)/g, "url('/");
    });
}
function AutoPreview({ type, label }) {
    const [html, setHtml] = useState("");
    useEffect(() => { liveSection(type).then(setHtml); }, [type]);
    return (
        <div className="pst-auto">
            <span className="pst-auto-tag">{label} · se actualiza solo</span>
            {html ? <div dangerouslySetInnerHTML={{ __html: html }} /> : <div className="pst-auto-empty">{label}</div>}
        </div>
    );
}

// ---------------------------------------------------------------- aplicación
const DICTIONARY = {
    "header-publish": "Publicar", "header-undo": "deshacer", "header-redo": "rehacer",
    "header-toggle-leftsidebar": "Mostrar u ocultar la columna izquierda", "header-toggle-rightsidebar": "Mostrar u ocultar la columna derecha",
    "action-selectparent": "Seleccionar el bloque que lo contiene", "action-drag": "Arrastra para cambiar el orden",
    "action-duplicate": "Duplicar", "action-delete": "Borrar", "label-page": "Página", "label-component": "Bloque",
    "outline-empty": "No hay bloques", "outline-header-title": "Estructura", "outline-item-duplicate": "Duplicar", "outline-item-delete": "Borrar",
    "drawer-category-other": "Otros", "field-arrayitem-summary": "Elemento {index}", "field-arrayitem-duplicate": "Duplicar",
    "field-arrayitem-delete": "Borrar", "plugin-blocks": "Bloques", "plugin-outline": "Estructura", "plugin-fields": "Campos",
    "plugin-components": "Bloques", "loader-loading": "cargando",
};
const VIEWPORTS = [
    { width: 390, height: "auto", icon: "Smartphone", label: "Móvil" },
    { width: 820, height: "auto", icon: "Tablet", label: "Tableta" },
    { width: 1280, height: "auto", icon: "Monitor", label: "Ordenador" },
];

function App() {
    const [state, setState] = useState({ status: "cargando" });
    const [toast, setToast] = useState("");
    const shas = useRef({ main: null, draft: null });
    const current = useRef(null);

    useEffect(() => {
        (async () => {
            if (!token()) return setState({ status: "sin-sesion" });
            try {
                const [datos, main, draft] = await Promise.all([
                    fetch("/admin/editor/datos.json", { cache: "no-store" }).then((r) => r.json()),
                    getFile(MAIN), getFile(DRAFT),
                ]);
                shas.current = { main: main && main.sha, draft: draft && draft.sha };
                const data = JSON.parse((draft || main || { text: '{"content":[],"root":{"props":{}}}' }).text);
                current.current = data;
                setState({ status: "listo", datos, data, hasDraft: !!draft });
            } catch (e) {
                setState({ status: e.message === "sesion" ? "sin-sesion" : "error" });
            }
        })();
    }, []);

    const config = useMemo(() => {
        if (state.status !== "listo") return null;
        const render = makeRenderer(makeFilters("/", state.datos.iconos, imgUrl), state.datos.globales);
        const cfg = makeConfig({
            render: (type, props) => render(TEMPLATES[type], props),
            imageField: (label) => ({ type: "custom", label, render: ({ value, onChange }) => <ImageField label={label} value={value} onChange={onChange} /> }),
            autoPreview: (type, label) => <AutoPreview type={type} label={label} />,
        });
        cfg.components.TarjetasIcono.fields.tarjetas.arrayFields.icono.options =
            Object.keys(state.datos.iconos).map((k) => ({ label: ICON_NAMES[k] || k, value: k }));
        return cfg;
    }, [state.status]);

    function flash(t) { setToast(t); setTimeout(() => setToast(""), 4000); }
    function failed(e) {
        if (e.message === "sesion") flash("La sesión ha caducado: vuelve a entrar en el panel (se abre en otra pestaña) y repite.");
        else if (e.message === "conflicto") flash("Alguien ha guardado esta página a la vez. Recarga la página para ver su versión.");
        else flash("No se ha podido guardar. Inténtalo de nuevo.");
    }
    const json = (d) => b64enc(JSON.stringify(d, null, 2) + "\n");

    async function saveDraft() {
        try {
            shas.current.draft = await putFile(DRAFT, json(current.current), `Borrador de «${PAGE}» guardado desde el editor visual — por ${who()}`, shas.current.draft);
            setState((s) => ({ ...s, hasDraft: true }));
            flash("✓ Borrador guardado. La web no cambia hasta que pulses «Publicar».");
        } catch (e) { failed(e); }
    }
    async function discardDraft() {
        if (!confirm("¿Descartar el borrador y volver a la versión publicada?")) return;
        try {
            await deleteFile(DRAFT, shas.current.draft, `Borrador de «${PAGE}» descartado — por ${who()}`);
            location.reload();
        } catch (e) { failed(e); }
    }
    async function publish(data) {
        if (!confirm("¿Publicar los cambios? La web se actualizará en uno o dos minutos.")) return;
        try {
            shas.current.main = await putFile(MAIN, json(data), `Página «${PAGE}» actualizada desde el editor visual — por ${who()}`, shas.current.main);
            if (shas.current.draft) {
                await deleteFile(DRAFT, shas.current.draft, `Borrador de «${PAGE}» publicado — por ${who()}`).catch(() => {});
                shas.current.draft = null;
            }
            setState((s) => ({ ...s, hasDraft: false }));
            flash("✓ Publicado. En uno o dos minutos lo verás en la web.");
        } catch (e) { failed(e); }
    }

    if (state.status === "cargando") return <div className="pst-screen">Cargando el editor…</div>;
    if (state.status === "sin-sesion") return (
        <div className="pst-screen">
            <h1>Editor visual de la web</h1>
            <p>Para editar las páginas, entra primero en el panel con tu usuario y vuelve a esta pestaña.</p>
            <p><a className="pst-btn" href="/admin/">Entrar en el panel</a> <button className="pst-btn" onClick={() => location.reload()}>Ya he entrado</button></p>
        </div>
    );
    if (state.status === "error") return <div className="pst-screen">No se ha podido cargar la página. Recarga dentro de un momento.</div>;

    return (
        <>
            <Puck
                config={config}
                data={state.data}
                onChange={(d) => { current.current = d; }}
                onPublish={publish}
                dictionary={DICTIONARY}
                viewports={VIEWPORTS}
                headerTitle={PAGE === "portada" ? "Portada" : PAGE}
                iframe={{ enabled: true, syncHostStyles: true }}
                overrides={{
                    // dentro de la vista previa se cargan los estilos de la web (fuera, el editor usa los suyos)
                    iframe: ({ children, document: doc }) => {
                        useEffect(() => {
                            if (!doc) return;
                            ["/css/fonts.css", "/css/site.css", "/admin/editor/vista.css"].forEach((href) => {
                                if (doc.head.querySelector(`link[data-pst="${href}"]`)) return;
                                const l = doc.createElement("link");
                                l.rel = "stylesheet"; l.href = href; l.setAttribute("data-pst", href);
                                doc.head.appendChild(l);
                            });
                        }, [doc]);
                        return children;
                    },
                    headerActions: ({ children }) => (
                        <>
                            {state.hasDraft && <span className="pst-draft">Borrador sin publicar</span>}
                            <a className="pst-btn pst-btn-ghost" href={PAGE === "portada" ? "/" : `/html/${PAGE}.html`} target="_blank" rel="noopener">Ver la web</a>
                            {state.hasDraft && <button className="pst-btn pst-btn-ghost" onClick={discardDraft}>Descartar borrador</button>}
                            <button className="pst-btn pst-btn-ghost" onClick={saveDraft}>Guardar borrador</button>
                            {children}
                        </>
                    ),
                }}
            />
            {toast && <div className="pst-toast" role="status">{toast}</div>}
        </>
    );
}

createRoot(document.getElementById("editor")).render(<App />);
