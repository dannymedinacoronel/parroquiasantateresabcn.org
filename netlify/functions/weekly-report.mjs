// Informe semanal de visitas por correo: cada lunes a las 8:07 (hora de Barcelona en invierno; 9:07 en verano)
// resume la semana anterior (de lunes a domingo) con los recuentos anónimos de hit.mjs y lo envía a la parroquia.
// El correo sale por FormSubmit, como los formularios de la web: la primera vez FormSubmit manda a esa dirección
// un mensaje para confirmarla («Activate form») y, una vez confirmada, los informes llegan solos.
import { getStore } from "@netlify/blobs";
import { STORE, madrid } from "./hit.mjs";
import { rollup, emptyAgg, merge } from "./visit-stats.mjs";

const TO = "parroquisantateresabarcelona@gmail.com";
const SITE = "https://parroquiasantateresabcn.netlify.app";
const DEVS = { movil: "móvil", tablet: "tableta", ordenador: "ordenador" };

const dayAdd = (day, n) => new Date(Date.parse(day + "T12:00:00Z") + n * 864e5).toISOString().slice(0, 10);
const fmt = (day, opts) => new Date(day + "T12:00:00Z").toLocaleDateString("es-ES", Object.assign({ timeZone: "UTC" }, opts));
const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);

async function week(store, from) {
    const a = emptyAgg();
    for (let i = 0; i < 7; i++) merge(a, (await store.get(`r/${dayAdd(from, i)}`, { type: "json" })) || emptyAgg());
    return a;
}

export function report(cur, prev, from) {
    const to = dayAdd(from, 6);
    const change = prev.entries ? Math.round((cur.entries - prev.entries) / prev.entries * 100) : null;
    const pages = top(cur.pages, 5).map(([p, n], i) => `${i + 1}. ${p === "/" ? "Portada" : p.replace(/^\/(ca|en)?\/?html\//, "$1 ").trim()} (${n})`).join("\n");
    const devs = top(cur.devs, 3).map(([d, n]) => `${DEVS[d] || d}: ${Math.round(n / (cur.views || 1) * 100)} %`).join(" · ");
    return {
        _subject: `Visitas a la web de la parroquia: ${cur.entries} esta semana`,
        _template: "box",
        _captcha: "false",
        Semana: `Del ${fmt(from, { day: "numeric", month: "long" })} al ${fmt(to, { day: "numeric", month: "long", year: "numeric" })}`,
        "Visitas (personas que entraron en la web)": String(cur.entries),
        "Páginas vistas": String(cur.views),
        "Respecto a la semana anterior": change === null ? "Sin datos de la semana anterior" : `${change >= 0 ? "+" : ""}${change} % (${prev.entries} visitas)`,
        "Páginas más vistas": pages || "—",
        "Desde qué aparato": devs || "—",
        "Ver todas las estadísticas": `${SITE}/admin/dashboard.html#visitas`,
    };
}

export default async () => {
    const store = getStore({ name: STORE, consistency: "strong" });
    const today = madrid().day;
    await rollup(store, today);
    // lunes de la semana pasada: hoy es lunes, así que la semana pasada empezó hace 7 días
    const back = (new Date(today + "T12:00:00Z").getUTCDay() + 6) % 7 + 7;
    const from = dayAdd(today, -back);
    const body = report(await week(store, from), await week(store, dayAdd(from, -7)), from);
    const res = await fetch(`https://formsubmit.co/ajax/${TO}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json", Origin: SITE, Referer: SITE + "/" },
        body: JSON.stringify(body),
    });
    console.log("informe semanal", from, res.status, (await res.text()).slice(0, 200));
};

export const config = { schedule: "7 7 * * 1" };
