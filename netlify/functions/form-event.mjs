// Métricas anónimas de los formularios de la web (sin cookies ni datos personales).
// La web envía: { form, type, purpose, lang }  ->  se guarda un evento en Netlify Blobs.
//   form:    contacto | comuniones
//   type:    view (se ha visto el formulario) | start (se ha empezado a rellenar) |
//            submit (enviado) | error (no se pudo enviar)
//   purpose: motivo del mensaje o curso escolar (lo que el formulario marca como «propósito»)
// Cada evento es una entrada propia cuyo nombre ya contiene todos los datos, así no se pisan
// aunque lleguen dos a la vez, y el panel los cuenta sin tener que abrirlos.
import { getStore } from "@netlify/blobs";

const FORMS = new Set(["contacto", "comuniones"]);
const TYPES = new Set(["view", "start", "submit", "error"]);
const LANGS = new Set(["es", "ca", "en"]);
const CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
};

// texto -> trozo seguro para el nombre del evento (sin acentos, espacios ni barras)
export function clean(s) {
    return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
        .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40) || "-";
}

export function eventKey(body, now = new Date()) {
    const form = clean(body.form), type = clean(body.type);
    if (!FORMS.has(form) || !TYPES.has(type)) return null;
    const lang = LANGS.has(body.lang) ? body.lang : "es";
    const day = now.toISOString().slice(0, 10);
    // los eventos de prueba («test: true») se guardan aparte y no cuentan en el panel
    const prefix = body.test === true ? "t" : "e";
    return `${prefix}/${day}/${form}/${type}/${clean(body.purpose)}/${lang}/${now.getTime()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default async (req) => {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (req.method !== "POST") return new Response("Método no permitido", { status: 405, headers: CORS });
    let body = {};
    try { body = JSON.parse(await req.text()); } catch (e) { /* cuerpo vacío o no válido */ }
    const key = eventKey(body);
    if (!key) return new Response("Datos no válidos", { status: 400, headers: CORS });
    await getStore("metricas-formularios").set(key, "1");
    return new Response(null, { status: 204, headers: CORS });
};

export const config = { path: "/api/form-event" };
