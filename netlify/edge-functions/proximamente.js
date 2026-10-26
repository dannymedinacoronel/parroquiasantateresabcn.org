// Web en pausa: mientras PROXIMAMENTE sea true, los visitantes solo ven la portada
// «Próximamente» (proximamente.html), en cualquier dirección de la web.
// El equipo sigue viendo la web completa:
//   - al entrar en el panel /admin/ con su usuario (el panel deja una cookie en el navegador), o
//   - abriendo una vez cualquier página con ?vista=santateresa1923 (por ejemplo, para enseñarla).
// Con ?vista=salir se quita la cookie y se vuelve a ver la portada, como un visitante.
// Para abrir la web a todo el mundo: PROXIMAMENTE = false (o borrar este archivo).
const PROXIMAMENTE = true;
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
    // solo las páginas: hojas de estilo, fotos, fuentes, etc. se sirven normal
    const p = url.pathname;
    const isPage = p.endsWith("/") || p.endsWith(".html") || !/\.[a-z0-9]+$/i.test(p);
    if (!isPage) return;
    return new URL("/proximamente.html", request.url);
};

export const config = {
    path: "/*",
    excludedPath: ["/admin/*", "/api/*", "/.netlify/*", "/proximamente.html", "/googlec43bda0c51371953.html"],
};
