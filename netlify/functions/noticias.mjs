// Noticias del Vaticano y del Arzobispado, siempre al día y sin GitHub Actions.
// Responde en la misma dirección que antes usaba el archivo estático (/data/noticias.js), así que las
// páginas no cambian: el navegador recibe «window.NOTICIAS = {...}» como siempre.
// La respuesta se guarda 3 horas en la caché de Netlify: la función solo se ejecuta unas pocas veces al día,
// por muchas visitas que haya. Si una fuente falla, se usan sus últimas noticias buenas (guardadas en Blobs).
// Hace lo mismo que scripts/actualizar_noticias.py (que se puede seguir usando a mano).
import { getStore } from "@netlify/blobs";

const PER_SOURCE = 8;
const UA = "Mozilla/5.0 (compatible; ParroquiaSantaTeresaBCN/1.0; +https://parroquiasantateresabcn.netlify.app/)";
const SOURCES = {
    vaticano_es: ["rss", "https://www.vaticannews.va/es.rss.xml"],
    vaticano_en: ["rss", "https://www.vaticannews.va/en.rss.xml"],
    arzobispado_ca: ["wp", "https://esglesia.barcelona/wp-json/wp/v2/ebn-actualitat"],
    arzobispado_es: ["wp", "https://esglesia.barcelona/es/wp-json/wp/v2/ebn-actualitat"],
};
const ENT = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", laquo: "«", raquo: "»", hellip: "…", ndash: "–", mdash: "—", rsquo: "’", lsquo: "‘", rdquo: "”", ldquo: "“" };

export function unescape(s) {
    return String(s || "").replace(/&(#x[0-9a-f]+|#\d+|\w+);/gi, (m, e) => {
        if (e[0] === "#") { const n = e[1].toLowerCase() === "x" ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10); return isNaN(n) ? m : String.fromCodePoint(n); }
        return ENT[e.toLowerCase()] ?? m;
    });
}
export function plain(s, limit = 190) {
    s = String(s || "").replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1");
    s = unescape(unescape(s).replace(/<[^>]+>/g, " ")).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    if (s.length > limit) s = s.slice(0, limit).replace(/\s+\S*$/, "").replace(/[,.;:]+$/, "") + "…";
    return s;
}
const tag = (xml, name) => { const m = xml.match(new RegExp(`<${name}\\b[^>]*>([\\s\\S]*?)</${name}>`, "i")); return m ? m[1] : ""; };
const https = (u) => (String(u || "").trim().startsWith("https://") ? String(u).trim() : "");

async function get(url) {
    const r = await fetch(url, { headers: { "User-Agent": UA }, signal: AbortSignal.timeout(7000) });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.text();
}
export function parseRss(xml) {
    return (xml.match(/<item\b[\s\S]*?<\/item>/gi) || []).map((it) => {
        const d = new Date(plain(tag(it, "pubDate"), 80));
        const media = it.match(/<media:content\b[^>]*\burl="([^"]+)"/i);
        return {
            titulo: plain(tag(it, "title"), 160),
            enlace: https(plain(tag(it, "link"), 500)),
            fecha: isNaN(d) ? null : d.toISOString().replace(".000Z", "+00:00"),
            resumen: plain(tag(it, "description")),
            imagen: https(media ? unescape(media[1]) : ""),
        };
    });
}
export function parseWp(json) {
    return JSON.parse(json).map((p) => ({
        titulo: plain(p.title && p.title.rendered, 160),
        enlace: https(p.link),
        fecha: p.date_gmt ? p.date_gmt + "+00:00" : null,
        resumen: plain(p.excerpt && p.excerpt.rendered),
        imagen: https(((p.yoast_head_json || {}).og_image || [{}])[0].url),
    }));
}

export default async () => {
    const store = getStore("noticias");
    const previous = (await store.get("ultimas", { type: "json" }).catch(() => null)) || {};
    const out = { actualizado: new Date().toISOString().slice(0, 16) + "+00:00" };
    let ok = 0;
    await Promise.all(Object.entries(SOURCES).map(async ([key, [kind, url]]) => {
        try {
            const items = kind === "rss" ? parseRss(await get(url)) : parseWp(await get(`${url}?per_page=${PER_SOURCE}&_fields=date_gmt,link,title,excerpt,yoast_head_json.og_image`));
            out[key] = items.filter((i) => i.titulo && i.enlace).slice(0, PER_SOURCE);
            if (out[key].length) ok++; else out[key] = previous[key] || [];
        } catch (e) {
            console.log("noticias:", key, String(e));
            out[key] = previous[key] || [];
        }
    }));
    if (ok) await store.setJSON("ultimas", out).catch(() => {});
    else if (previous.actualizado) out.actualizado = previous.actualizado;
    return new Response("/* Noticias del Vaticano y del Arzobispado (netlify/functions/noticias.mjs) */\nwindow.NOTICIAS = " + JSON.stringify(out) + ";\n", {
        headers: {
            "Content-Type": "application/javascript; charset=utf-8",
            "Cache-Control": "public, max-age=900",
            // caché de Netlify: 3 horas, y mientras se renueva se sigue sirviendo la anterior
            "Netlify-CDN-Cache-Control": ok ? "public, durable, s-maxage=10800, stale-while-revalidate=86400" : "public, durable, s-maxage=600",
        },
    });
};

export const config = { path: "/data/noticias.js" };
