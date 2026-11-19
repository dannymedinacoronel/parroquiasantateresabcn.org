// Cápsulas de fe automáticas: los reels de Instagram de la parroquia que llevan #CápsulasDeFe en el texto.
// GET /api/capsulas-ig      -> lista de reels (la web los añade sola a la portada y a «Cápsulas de fe»)
// GET /api/ig-thumb?id=...  -> foto de portada del reel, guardada aquí (la web no pide nada a Instagram al cargar)
// Necesita la clave de la API de Instagram en la variable IG_TOKEN de Netlify (cuenta profesional).
// La clave dura 60 días: esta función la renueva sola cada 20 días y guarda la nueva en Blobs.
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
    let tok = await store.get("token", { type: "json" }).catch(() => null);
    if (!tok && process.env.IG_TOKEN) tok = { t: process.env.IG_TOKEN, at: 0 };
    if (!tok) return reply([], 3600);
    if (Date.now() - (tok.at || 0) > 20 * 864e5) {
        try {
            const r = await fetch(`https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(tok.t)}`);
            if (r.ok) { tok = { t: (await r.json()).access_token, at: Date.now() }; await store.setJSON("token", tok); }
        } catch (e) { console.log("ig: no se pudo renovar la clave", String(e)); }
    }
    try {
        const r = await fetch(`https://graph.instagram.com/me/media?fields=id,caption,media_type,permalink,thumbnail_url,timestamp&limit=50&access_token=${encodeURIComponent(tok.t)}`,
            { signal: AbortSignal.timeout(8000) });
        const j = await r.json();
        if (!r.ok) throw new Error(JSON.stringify(j.error || j).slice(0, 200));
        const items = [];
        for (const m of j.data || []) {
            if (m.media_type !== "VIDEO" || !TAG.test(m.caption || "")) continue;
            if (m.thumbnail_url && !(await store.getMetadata("thumb/" + m.id).catch(() => null))) {
                const im = await fetch(m.thumbnail_url).catch(() => null);
                if (im && im.ok) await store.set("thumb/" + m.id, await im.arrayBuffer());
            }
            items.push({ id: m.id, link: m.permalink, titulo: titleOf(m.caption), tema: temaOf(m.caption), fecha: (m.timestamp || "").slice(0, 10), foto: `/api/ig-thumb?id=${m.id}` });
        }
        await store.setJSON("ultimas", items);
        return reply(items, 3 * 3600);
    } catch (e) {
        console.log("ig:", String(e));
        return reply((await store.get("ultimas", { type: "json" }).catch(() => null)) || [], 600);
    }
};

export const config = { path: ["/api/capsulas-ig", "/api/ig-thumb"] };
