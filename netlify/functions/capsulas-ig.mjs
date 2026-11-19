// Cápsulas de fe automáticas: los reels de Instagram de la parroquia que llevan #CápsulasDeFe en el texto.
// GET /api/capsulas-ig      -> lista de reels (la web los añade sola a la portada y a «Cápsulas de fe»)
// GET /api/ig-thumb?id=...  -> foto de portada del reel, guardada aquí (la web no pide nada a Instagram al cargar)
// GET /api/ig-video?id=...  -> el vídeo del reel, guardado aquí, para verlo con el reproductor de la web (por trozos)
// Dos formas de conectarlo (las dos con la cuenta de Instagram en modo profesional):
//  - BEHOLD_FEED: el enlace del feed JSON de behold.so (gratis; solo hay que conectar Instagram en su web), o
//  - IG_TOKEN: la clave de la API de Instagram (dura 60 días; esta función la renueva sola cada 20 días).
// Los reels encontrados se guardan en Blobs, así no se pierden aunque el feed solo traiga los últimos.
const BEHOLD_FEED = process.env.BEHOLD_FEED || "";
import { getStore } from "@netlify/blobs";

const TAG = /#c[aá]psulasdefe\b/i;
const TEMAS = [[/#?(adviento|navidad|cuaresma|pascua|liturgia)/i, "Liturgia"], [/#?(eucarist|sacrament|confesi|bautis|perd[oó]n)/i, "Sacramentos"],
    [/#?(santateresa|nadateturbe|teresa)/i, "Santa Teresa"], [/#?(oraci[oó]n|rezar)/i, "Oración"], [/#?(biblia|evangelio)/i, "Biblia"]];

const reply = (body, secs) => new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "public, max-age=600",
        "Netlify-CDN-Cache-Control": `public, durable, s-maxage=${secs}, stale-while-revalidate=86400` },
});

export function titleOf(caption) {
    const first = String(caption || "").split("\n").map((l) => l.replace(/#\S+/g, "").replace(/[\p{Extended_Pictographic}️‍]/gu, "").trim()).find(Boolean) || "Cápsula de fe";
    return first.replace(/^[«"]|[»"]$/g, "").slice(0, 70);
}
export const temaOf = (caption) => (TEMAS.find(([re]) => re.test(caption || "")) || [null, "Vida cristiana"])[1];

export default async (req) => {
    const url = new URL(req.url);
    const store = getStore("instagram");
    if (url.pathname.endsWith("/ig-thumb")) {
        const id = (url.searchParams.get("id") || "").replace(/\D/g, "");
        const img = id && (await store.get("thumb/" + id, { type: "arrayBuffer" }).catch(() => null));
        if (!img) return new Response("", { status: 404 });
        return new Response(img, { headers: { "Content-Type": "image/jpeg", "Cache-Control": "public, max-age=86400", "Netlify-CDN-Cache-Control": "public, durable, s-maxage=2592000" } });
    }
    if (url.pathname.endsWith("/ig-video")) {
        const id = (url.searchParams.get("id") || "").replace(/\D/g, "");
        const buf = id && (await store.get("video/" + id, { type: "arrayBuffer" }).catch(() => null));
        if (!buf) return new Response("", { status: 404 });
        const size = buf.byteLength, CH = 3 * 1024 * 1024;
        const h = { "Content-Type": "video/mp4", "Accept-Ranges": "bytes", "Vary": "Range", "Cache-Control": "public, max-age=86400", "Netlify-CDN-Cache-Control": "no-store" };
        const m = /bytes=(\d*)-(\d*)/.exec(req.headers.get("range") || "");
        if (!m && size <= CH) return new Response(buf, { headers: { ...h, "Content-Length": String(size) } });
        const start = m && m[1] ? +m[1] : (m && m[2] ? Math.max(0, size - +m[2]) : 0);
        if (start >= size) return new Response("", { status: 416, headers: { "Content-Range": `bytes */${size}` } });
        const end = Math.min(m && m[1] && m[2] ? +m[2] : size - 1, start + CH - 1, size - 1);
        return new Response(buf.slice(start, end + 1), { status: 206, headers: { ...h, "Content-Range": `bytes ${start}-${end}/${size}`, "Content-Length": String(end - start + 1) } });
    }
    const saved = (await store.get("ultimas", { type: "json" }).catch(() => null)) || [];
    const keep = (found) => {
        const all = new Map(saved.map((x) => [x.id, x]));
        found.forEach((x) => all.set(x.id, x));
        return [...all.values()].sort((a, b) => (b.fecha || "").localeCompare(a.fecha || "")).slice(0, 60);
    };
    async function thumb(id, src) {
        if (!src || (await store.getMetadata("thumb/" + id).catch(() => null))) return;
        const im = await fetch(src).catch(() => null);
        if (im && im.ok) await store.set("thumb/" + id, await im.arrayBuffer());
    }
    let budget = 2; // como mucho 2 vídeos nuevos por llamada, para no pasar del tiempo de la función
    async function video(id, src) {
        if (await store.getMetadata("video/" + id).catch(() => null)) return `/api/ig-video?id=${id}`;
        if (!src || budget <= 0) return "";
        budget--;
        const r = await fetch(src, { signal: AbortSignal.timeout(9000) }).catch(() => null);
        if (!r || !r.ok) return "";
        const buf = await r.arrayBuffer();
        if (buf.byteLength > 40e6) return "";
        await store.set("video/" + id, buf);
        return `/api/ig-video?id=${id}`;
    }
    if (BEHOLD_FEED) {
        try {
            const r = await fetch(BEHOLD_FEED, { signal: AbortSignal.timeout(8000) });
            const j = await r.json();
            const found = [];
            for (const m of (j.posts || j || [])) {
                if (!/video|reel/i.test(m.mediaType || m.media_type || "") || !TAG.test(m.caption || "")) continue;
                const id = String(m.id || "").replace(/\D/g, "") || String(Math.abs([...String(m.permalink)].reduce((h, c) => (h * 31 + c.charCodeAt(0)) | 0, 0)));
                await thumb(id, m.thumbnailUrl || (m.sizes && m.sizes.medium && m.sizes.medium.mediaUrl) || m.mediaUrl);
                const vid = await video(id, m.mediaUrl);
                found.push({ id, video: vid, link: m.permalink, titulo: titleOf(m.caption), tema: temaOf(m.caption), fecha: (m.timestamp || "").slice(0, 10), foto: `/api/ig-thumb?id=${id}` });
            }
            const items = keep(found);
            await store.setJSON("ultimas", items);
            return reply(items, 3 * 3600);
        } catch (e) {
            console.log("behold:", String(e));
            return reply(saved, 600);
        }
    }
    let tok = await store.get("token", { type: "json" }).catch(() => null);
    if (!tok && process.env.IG_TOKEN) tok = { t: process.env.IG_TOKEN, at: 0 };
    if (!tok) return reply(saved, 3600);
    if (Date.now() - (tok.at || 0) > 20 * 864e5) {
        try {
            const r = await fetch(`https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(tok.t)}`);
            if (r.ok) { tok = { t: (await r.json()).access_token, at: Date.now() }; await store.setJSON("token", tok); }
        } catch (e) { console.log("ig: no se pudo renovar la clave", String(e)); }
    }
    try {
        const r = await fetch(`https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp&limit=50&access_token=${encodeURIComponent(tok.t)}`,
            { signal: AbortSignal.timeout(8000) });
        const j = await r.json();
        if (!r.ok) throw new Error(JSON.stringify(j.error || j).slice(0, 200));
        const items = [];
        for (const m of j.data || []) {
            if (m.media_type !== "VIDEO" || !TAG.test(m.caption || "")) continue;
            await thumb(m.id, m.thumbnail_url);
            items.push({ id: m.id, video: await video(m.id, m.media_url), link: m.permalink, titulo: titleOf(m.caption), tema: temaOf(m.caption), fecha: (m.timestamp || "").slice(0, 10), foto: `/api/ig-thumb?id=${m.id}` });
        }
        const all = keep(items);
        await store.setJSON("ultimas", all);
        return reply(all, 3 * 3600);
    } catch (e) {
        console.log("ig:", String(e));
        return reply((await store.get("ultimas", { type: "json" }).catch(() => null)) || [], 600);
    }
};

export const config = { path: ["/api/capsulas-ig", "/api/ig-thumb", "/api/ig-video"] };
