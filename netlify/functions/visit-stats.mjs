// Estadísticas de visitas para el dashboard (/admin/dashboard.html#visitas).
// GET /api/visit-stats?days=30   ->  resumen del periodo + hoy + ahora mismo
// GET /api/visit-stats?live=1    ->  solo hoy y ahora mismo (el dashboard lo pide cada 15 s)
// Solo recuentos anónimos: páginas, idiomas, dispositivos y webs de procedencia.
//
// Para que no se acumulen miles de entradas, cada día ya terminado se resume en una sola
// (r/<día>) la primera vez que se consultan las estadísticas, y se borran las visitas sueltas de ese día.
import { getStore } from "@netlify/blobs";
import { STORE, madrid } from "./hit.mjs";

const DEL_LIMIT = 400;   // borrados como mucho por consulta (el resto, en la siguiente)

export function emptyAgg() { return { views: 0, entries: 0, pages: {}, langs: {}, devs: {}, refs: {}, hours: {} }; }
function inc(o, k, n) { o[k] = (o[k] || 0) + (n || 1); }
export function parseView(key) {
    // v/<día>/<hora>/<ruta>/<idioma>/<dispositivo>/<procedencia>/<entrada>/<ms>-<azar>
    const p = key.split("/");
    if (p[0] !== "v" || p.length < 9) return null;
    return { day: p[1], hour: p[2], path: p[3].replace(/~/g, "/") || "/", lang: p[4], dev: p[5], ref: p[6], entry: p[7] === "1", ts: parseInt(p[8], 10) || 0 };
}
export function addView(a, v) {
    a.views++; if (v.entry) a.entries++;
    inc(a.pages, v.path); inc(a.langs, v.lang); inc(a.devs, v.dev); inc(a.hours, v.hour);
    if (v.entry) inc(a.refs, v.ref);
}
export function merge(a, b) {
    a.views += b.views || 0; a.entries += b.entries || 0;
    ["pages", "langs", "devs", "refs", "hours"].forEach((f) => { Object.keys(b[f] || {}).forEach((k) => inc(a[f], k, b[f][k])); });
    return a;
}
function dayList(since, until) {
    const out = [];
    for (let d = new Date(since + "T12:00:00Z"); d.toISOString().slice(0, 10) <= until; d = new Date(d.getTime() + 864e5)) out.push(d.toISOString().slice(0, 10));
    return out;
}
async function inBatches(items, n, fn) {
    const out = [];
    for (let i = 0; i < items.length; i += n) out.push(...await Promise.all(items.slice(i, i + n).map(fn)));
    return out;
}
const dirsOf = (res) => (res.directories || []).map((d) => d.replace(/\/+$/, "").split("/").pop());

// resume en r/<día> los días ya terminados y borra sus entradas sueltas (visitas y «sigo aquí»)
export async function rollup(store, today) {
    let budget = DEL_LIMIT;
    for (const day of dirsOf(await store.list({ prefix: "v/", directories: true })).filter((d) => d < today).sort()) {
        const { blobs } = await store.list({ prefix: `v/${day}/` });
        if (!await store.get(`r/${day}`)) {
            const a = emptyAgg();
            blobs.forEach((b) => { const v = parseView(b.key); if (v) addView(a, v); });
            await store.setJSON(`r/${day}`, a);
        }
        // todos los días quedan resumidos; lo que no da tiempo a borrar se borra en la siguiente consulta
        const del = blobs.slice(0, Math.max(0, budget));
        budget -= del.length;
        await inBatches(del, 50, (b) => store.delete(b.key));
    }
    if (budget <= 0) return;
    for (const day of dirsOf(await store.list({ prefix: "p/", directories: true })).filter((d) => d < today)) {
        const { blobs } = await store.list({ prefix: `p/${day}/` });
        const del = blobs.slice(0, budget);
        budget -= del.length;
        await inBatches(del, 50, (b) => store.delete(b.key));
        if (budget <= 0) return;
    }
}

export async function live(store, now = new Date()) {
    const t = madrid(now), ms = now.getTime();
    const { blobs } = await store.list({ prefix: `v/${t.day}/` });
    const today = emptyAgg(), recent = [];
    let last30 = 0, last30s = 0;
    blobs.forEach((b) => {
        const v = parseView(b.key); if (!v) return;
        addView(today, v);
        if (v.ts >= ms - 30 * 60e3) last30++;
        if (v.ts >= ms - 30e3) last30s++;
        recent.push(v);
    });
    recent.sort((a, b) => b.ts - a.ts);
    // personas ahora mismo: cada pestaña abierta avisa cada 30 s, así que en el último minuto
    // cuenta dos veces; se suman las que acaban de entrar y aún no han avisado
    const prev = new Date(ms - 70e3), tp = madrid(prev);
    const prefixes = [...new Set([`p/${t.day}/${t.hour}`, `p/${tp.day}/${tp.hour}`])];
    let pings = 0;
    for (const prefix of prefixes) {
        (await store.list({ prefix })).blobs.forEach((b) => { if ((parseInt(b.key.split("/")[3], 10) || 0) >= ms - 65e3) pings++; });
    }
    return {
        day: t.day,
        now: { active: Math.ceil(pings / 2) + last30s, last30, recent: recent.slice(0, 20).map(({ ts, path, lang, dev, ref, entry }) => ({ ts, path, lang, dev, ref, entry })) },
        today,
    };
}

export async function stats(store, days, now = new Date()) {
    const t = madrid(now);
    await rollup(store, t.day);
    const lv = await live(store, now);
    const since = madrid(new Date(now.getTime() - (days - 1) * 864e5)).day;
    const past = dayList(since, t.day).filter((d) => d < t.day);
    const rolled = await inBatches(past, 25, (d) => store.get(`r/${d}`, { type: "json" }).then((j) => j || emptyAgg()));
    const total = emptyAgg(), series = [];
    past.forEach((d, i) => { merge(total, rolled[i]); series.push({ day: d, views: rolled[i].views, entries: rolled[i].entries }); });
    merge(total, lv.today);
    series.push({ day: t.day, views: lv.today.views, entries: lv.today.entries });
    return Object.assign(lv, { since, days, series, total });
}

export default async (req) => {
    const url = new URL(req.url);
    // lectura «fuerte»: siempre lo último que ha llegado, sin el retraso de hasta 1 min de la caché
    const store = getStore({ name: STORE, consistency: "strong" });
    const headers = { "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" };
    if (url.searchParams.get("live") === "1") return Response.json(Object.assign({ generated: new Date().toISOString() }, await live(store)), { headers });
    const days = Math.min(400, Math.max(1, parseInt(url.searchParams.get("days") || "30", 10) || 30));
    return Response.json(Object.assign({ generated: new Date().toISOString() }, await stats(store, days)), { headers });
};

export const config = { path: "/api/visit-stats" };
