// Plantillas de los bloques del editor visual: el mismo «mustache» pequeño que scripts/generador/bloques.py
// (si se cambia uno, hay que cambiar el otro). Ver la explicación de la sintaxis en bloques.py.
const TAG = /\{\{(\{?)([#^/]?)\s*([^}]+?)\s*\}?\}\}/g;

export function esc(v) {
    return String(v == null ? "" : v).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

export function parse(tpl) {
    const root = [], stack = [];
    let cur = root, pos = 0, m;
    TAG.lastIndex = 0;
    while ((m = TAG.exec(tpl))) {
        if (m.index > pos) cur.push(tpl.slice(pos, m.index));
        const raw = m[1], kind = m[2], name = m[3].trim();
        pos = TAG.lastIndex;
        if (kind === "#" || kind === "^") {
            const node = [kind, name, []];
            cur.push(node);
            stack.push([cur, name]);
            cur = node[2];
        } else if (kind === "/") {
            const [parent] = stack.pop();
            cur = parent;
        } else {
            cur.push([raw ? "raw" : "var", name, null]);
        }
    }
    if (pos < tpl.length) cur.push(tpl.slice(pos));
    return root;
}

function lookup(stack, name) {
    for (let i = stack.length - 1; i >= 0; i--) {
        const c = stack[i];
        if (c && typeof c === "object" && !Array.isArray(c) && name in c) return c[name];
    }
    return "";
}
const truthy = (v) => (typeof v === "boolean" ? v : typeof v === "number" ? true : !!v);

export function makeRenderer(filters, globals) {
    const cache = new Map();
    function value(stack, expr) {
        const i = expr.indexOf("|");
        if (i < 0) return lookup(stack, expr.trim());
        return filters[expr.slice(i + 1).trim()](lookup(stack, expr.slice(0, i).trim()), stack);
    }
    function run(nodes, stack) {
        let out = "";
        for (const n of nodes) {
            if (typeof n === "string") { out += n; continue; }
            const [kind, name, kids] = n;
            if (kind === "var") { const v = value(stack, name); out += name.includes("|") ? v : esc(v); }
            else if (kind === "raw") out += String(value(stack, name) || "");
            else if (name.includes("=")) {
                const [k, want] = name.split("=").map((x) => x.trim());
                const show = String(lookup(stack, k)) === want;
                if ((kind === "#") === show) out += run(kids, stack);
            } else if (name.endsWith("?")) {
                const v = lookup(stack, name.slice(0, -1));
                const show = truthy(v) && !(Array.isArray(v) && !v.length);
                if ((kind === "#") === show) out += run(kids, stack);
            } else {
                const v = lookup(stack, name);
                if (kind === "^") { if (!truthy(v) || (Array.isArray(v) && !v.length)) out += run(kids, stack); }
                else if (Array.isArray(v)) v.forEach((item, i) => {
                    const meta = { "@index": i + 1, "@first": i === 0, "@last": i === v.length - 1 };
                    out += run(kids, stack.concat([meta, item && typeof item === "object" ? item : { ".": item }]));
                });
                else if (v && typeof v === "object") out += run(kids, stack.concat([v]));
                else if (truthy(v)) out += run(kids, stack);
            }
        }
        return out;
    }
    return (tpl, props) => {
        if (!cache.has(tpl)) cache.set(tpl, parse(tpl));
        return run(cache.get(tpl), [globals, props]);
    };
}

export function makeFilters(base, icons, imgUrl) {
    const img = (v) => {
        v = String(v || "").trim();
        if (!v) return "";
        if (/^(https?:)?\/\/|^\/|^data:|^blob:/.test(v)) return esc(v);
        return esc(base + "fotosdefinitivas/web/" + v);
    };
    const url = (v) => {
        v = String(v || "").trim();
        if (!v || /^(https?:|mailto:|tel:|#|\/)/.test(v)) return esc(v);
        return esc(base + v);
    };
    const p = (v) => String(v || "").split(/\n\s*\n/).map((x) => x.trim()).filter(Boolean).map((x) => "<p>" + esc(x).replace(/\n/g, "<br>") + "</p>").join("");
    const br = (v) => esc(String(v || "").trim()).replace(/\n/g, "<br>");
    const icon = (v) => icons[String(v || "")] || "";
    const count = (v) => {
        const m = /^(\+?)(\d+)$/.exec(String(v || "").trim());
        if (!m) return "";
        const n = parseInt(m[2], 10);
        return ` data-count="${n}"` + (m[1] ? ' data-prefix="+"' : "") + (n > 1850 && n < 2100 ? ' data-from="1850"' : "");
    };
    const im = imgUrl || img;
    return { img: im, hero: im, url, p, br, icon, count };
}
