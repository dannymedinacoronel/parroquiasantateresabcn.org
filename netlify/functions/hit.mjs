// Visitas anónimas de la web, sin cookies ni datos personales.
// Cada página vista envía: { k: "view", p: ruta, l: idioma, d: dispositivo, r: web de procedencia, e: 1 si entra desde fuera }
// y, mientras la pestaña está a la vista, un «sigo aquí» cada 30 s ({ k: "ping" }) para saber cuántas personas hay ahora mismo.
// No se guarda la IP, ni el navegador, ni nada que identifique a nadie: solo la página y esos datos generales.
// Cada visita es una entrada propia cuyo nombre ya contiene los datos (así no se pisan aunque lleguen a la vez).
import { getStore } from "@netlify/blobs";

export const STORE = "metricas-visitas";
const LANGS = new Set(["es", "ca", "en"]);
const DEVS = new Set(["movil", "tablet", "ordenador"]);
const BOTS = /bot|crawl|spider|slurp|preview|facebookexternalhit|headless|lighthouse|pingdom|monitor/i;
const CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
};

// fecha y hora de Barcelona: { day: "2026-10-21", hour: "14", hhmm: "1405" }
export function madrid(now = new Date()) {
    const s = new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Madrid", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(now);
    const [day, time] = s.split(" ");
    return { day, hour: time.slice(0, 2), hhmm: time.replace(":", "") };
}

// ruta de la página -> trozo seguro para el nombre ("/html/contacto" -> "html~contacto", "/" -> "~")
export function cleanPath(p) {
    p = String(p || "/").split(/[?#]/)[0].toLowerCase().replace(/\.html$/, "").replace(/\/index$/, "/");
    if (!/^\/[a-z0-9\-\/._%ñ]*$/.test(p) || p.length > 120) return null;
    return p.replace(/\/+$/, "").replace(/\//g, "~") || "~";
}
export function cleanRef(r) {
    r = String(r || "").toLowerCase().replace(/^www\./, "").replace(/[^a-z0-9.\-]/g, "").slice(0, 50);
    return r || "directo";
}

export function hitKey(body, now = new Date()) {
    const t = madrid(now), rnd = now.getTime() + "-" + Math.random().toString(36).slice(2, 8);
    if (body.k === "ping") return `p/${t.day}/${t.hhmm}/${rnd}`;
    if (body.k !== "view") return null;
    const path = cleanPath(body.p);
    if (!path) return null;
    const lang = LANGS.has(body.l) ? body.l : "es";
    const dev = DEVS.has(body.d) ? body.d : "ordenador";
    return `v/${t.day}/${t.hour}/${path}/${lang}/${dev}/${cleanRef(body.r)}/${body.e ? 1 : 0}/${rnd}`;
}

export default async (req) => {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (req.method !== "POST") return new Response("Método no permitido", { status: 405, headers: CORS });
    if (BOTS.test(req.headers.get("user-agent") || "")) return new Response(null, { status: 204, headers: CORS });
    let body = {};
    try { body = JSON.parse(await req.text()); } catch (e) { /* cuerpo vacío o no válido */ }
    const key = hitKey(body);
    if (!key) return new Response("Datos no válidos", { status: 400, headers: CORS });
    await getStore(STORE).set(key, "1");
    return new Response(null, { status: 204, headers: CORS });
};

export const config = { path: "/api/hit" };
