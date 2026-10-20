// Estadísticas agregadas de los formularios para el panel /admin/metricas.html.
// GET /api/form-stats?days=90  ->  { since, days, generated, counts: { "día|formulario|tipo|propósito|idioma": n } }
// Solo contiene recuentos anónimos: ningún nombre, correo ni mensaje.
import { getStore } from "@netlify/blobs";

export function aggregate(keys, since) {
    const counts = {};
    for (const k of keys) {
        const [, day, form, type, purpose, lang] = k.split("/");
        if (!day || day < since) continue;
        const id = [day, form, type, purpose, lang].join("|");
        counts[id] = (counts[id] || 0) + 1;
    }
    return counts;
}

export default async (req) => {
    const url = new URL(req.url);
    const days = Math.min(400, Math.max(1, parseInt(url.searchParams.get("days") || "90", 10) || 90));
    const since = new Date(Date.now() - (days - 1) * 864e5).toISOString().slice(0, 10);
    // ?test=1 muestra solo los eventos de prueba (para comprobar que todo funciona sin mezclar cifras)
    const prefix = url.searchParams.get("test") === "1" ? "t/" : "e/";
    const { blobs } = await getStore("metricas-formularios").list({ prefix });
    return Response.json(
        { since, days, generated: new Date().toISOString(), counts: aggregate(blobs.map((b) => b.key), since) },
        { headers: { "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" } }
    );
};

export const config = { path: "/api/form-stats" };
