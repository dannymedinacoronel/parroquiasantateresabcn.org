// Revista en «Próximamente» (casilla del panel: Revista · Recuadro de la portada).
// Mientras esté activada, los números y artículos (html/revista/...) no se enseñan a los visitantes:
// se les lleva a la página Revista, que muestra «Próximamente». El equipo sí los ve:
//   - al entrar en el panel /admin/ con su usuario (el panel deja una cookie en el navegador), o
//   - abriendo una vez cualquier número con ?vista=santateresa1923 (por ejemplo, para enseñarlo).
// Con ?vista=salir se quita la cookie. estado.js lo escribe el generador a partir del panel.
import { PROXIMAMENTE } from "./estado.js";

const CLAVE = "santateresa1923";
const COOKIE = "pst_vista";

export default async (request, context) => {
    if (!PROXIMAMENTE) return;
    const url = new URL(request.url);
    const vista = url.searchParams.get("vista");
    if (vista === CLAVE || vista === "salir") {
        url.searchParams.delete("vista");
        const headers = new Headers({ Location: url.pathname + url.search, "Cache-Control": "no-store" });
        headers.append("Set-Cookie", vista === "salir"
            ? `${COOKIE}=; Path=/; Max-Age=0; SameSite=Lax; Secure`
            : `${COOKIE}=1; Path=/; Max-Age=31536000; SameSite=Lax; Secure`);
        return new Response(null, { status: 302, headers });
    }
    if (context.cookies.get(COOKIE) === "1") return;
    const lang = (url.pathname.match(/^\/(ca|en)\//) || [])[1];
    return new Response(null, {
        status: 302,
        headers: { Location: (lang ? `/${lang}` : "") + "/html/revista.html", "Cache-Control": "no-store" },
    });
};

export const config = {
    path: ["/html/revista/*", "/ca/html/revista/*", "/en/html/revista/*"],
};
