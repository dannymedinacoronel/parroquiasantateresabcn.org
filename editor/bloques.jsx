// Bloques del editor visual: qué campos tiene cada uno y cómo se pinta (con su plantilla de editor/plantillas/,
// la misma que usa el generador de la web: scripts/generador/bloques.py).
import React from "react";
import Carrusel from "./plantillas/Carrusel.html";
import TextoFoto from "./plantillas/TextoFoto.html";
import BandaFrase from "./plantillas/BandaFrase.html";
import TarjetasFoto from "./plantillas/TarjetasFoto.html";
import TarjetasIcono from "./plantillas/TarjetasIcono.html";
import Galeria from "./plantillas/Galeria.html";
import Visita from "./plantillas/Visita.html";
import Texto from "./plantillas/Texto.html";
import Cita from "./plantillas/Cita.html";
import Llamada from "./plantillas/Llamada.html";
import Video from "./plantillas/Video.html";
import Columnas from "./plantillas/Columnas.html";
import Separador from "./plantillas/Separador.html";

export const TEMPLATES = { Carrusel, TextoFoto, BandaFrase, TarjetasFoto, TarjetasIcono, Galeria, Visita, Texto, Cita, Llamada, Video, Columnas, Separador };

// ---------------------------------------------------------------- miniaturas de los bloques (columna izquierda)
const G = "#bfa065", L = "#e8dcc2", D = "#cdbf9f";
const box = (x, y, w, h, f = L, r = 3) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${f}"/>`;
const lines = (x, y, w, n, gap = 6) => Array.from({ length: n }, (_, i) => box(x, y + i * gap, i === n - 1 ? w * 0.6 : w, 3, D, 1.5)).join("");
const THUMB = {
    Carrusel: box(0, 0, 120, 70, "#6d5326", 6) + box(30, 22, 60, 7, "#fff", 2) + box(42, 34, 36, 3, "#f3e7c9", 1.5) + box(38, 46, 20, 7, G, 2) + box(62, 46, 20, 7, "none") + `<circle cx="54" cy="63" r="2" fill="#fff"/><circle cx="60" cy="63" r="2" fill="#fff8"/><circle cx="66" cy="63" r="2" fill="#fff8"/>`,
    TextoFoto: box(8, 12, 46, 46, "#d9c9a5", 4) + box(64, 16, 30, 5, G, 2) + lines(64, 28, 48, 4) + box(64, 52, 22, 7, G, 2),
    Texto: box(40, 10, 40, 5, G, 2) + lines(20, 24, 80, 5),
    Columnas: [8, 46, 84].map((x) => box(x, 12, 28, 46, "#fff", 4) + box(x + 4, 18, 14, 4, G, 2) + lines(x + 4, 28, 20, 4, 5)).join(""),
    Visita: box(8, 10, 40, 50, "#d9c9a5", 4) + box(58, 14, 34, 5, G, 2) + lines(58, 26, 52, 3) + box(58, 48, 26, 7, G, 2),
    BandaFrase: box(0, 6, 120, 58, "#8f7340", 4) + box(26, 26, 68, 4, "#fff", 2) + box(36, 34, 48, 4, "#fff", 2) + box(48, 44, 24, 3, "#f3e7c9", 1.5),
    Cita: box(30, 18, 60, 6, D, 3) + box(38, 28, 44, 6, D, 3) + box(48, 42, 24, 3, G, 1.5),
    Llamada: box(14, 10, 92, 50, "#fbf5e8", 6) + box(40, 18, 40, 5, G, 2) + lines(30, 28, 60, 2) + box(46, 44, 28, 8, G, 3),
    TarjetasFoto: [6, 34, 62, 90].map((x) => box(x, 10, 24, 50, "#fff", 3) + box(x, 10, 24, 22, "#d9c9a5", 3) + lines(x + 3, 38, 18, 3, 5)).join(""),
    TarjetasIcono: [8, 46, 84].map((x) => box(x, 12, 28, 46, "#fff", 4) + `<circle cx="${x + 14}" cy="26" r="7" fill="#f3e7c9" stroke="${G}"/>` + lines(x + 4, 40, 20, 2, 6)).join(""),
    Galeria: box(6, 8, 52, 26, "#d9c9a5") + box(62, 8, 24, 54, "#c9b48a") + box(90, 8, 24, 26, "#d9c9a5") + box(6, 38, 24, 24, "#c9b48a") + box(34, 38, 24, 24, "#d9c9a5") + box(90, 38, 24, 24, "#c9b48a"),
    Video: box(14, 8, 92, 54, "#2a241c", 5) + `<path d="M54 24l16 11-16 11z" fill="${G}"/>`,
    Separador: box(10, 34, 40, 2, D, 1) + box(70, 34, 40, 2, D, 1) + `<circle cx="60" cy="35" r="4" fill="none" stroke="${G}"/>`,
};
const AUTO_THUMB = box(6, 8, 108, 54, "#f6f0e3", 6) + `<path d="M48 35a12 12 0 1 1 3.5 8.5M48 44v-9h9" fill="none" stroke="${G}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>` + box(66, 30, 30, 4, D, 2) + box(66, 38, 22, 4, D, 2);
export function thumb(name) {
    return `<svg viewBox="0 0 120 70" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${THUMB[name] || AUTO_THUMB}</svg>`;
}

// ---- campos reutilizables
// texto en castellano + traducción opcional (català / English) debajo
let ADV = false;   // «Más opciones»: traducciones y campos técnicos
const adv = (o) => (ADV ? o : {});
export function tx(name, label, type = "text") {
    if (!ADV) return { [name]: { type, label } };
    return {
        [name]: { type, label },
        [name + "_tr"]: {
            type: "object", label: "↳ Traducción (opcional)",
            objectFields: { ca: { type, label: "Català" }, en: { type, label: "English" } },
        },
    };
}
const FONDO = {
    fondo: {
        type: "select", label: "Color de fondo",
        options: [{ label: "Claro", value: "" }, { label: "Cálido (beige)", value: "section-warm" }, { label: "Gris muy claro", value: "section-alt" }],
    },
};
const ANCLA_F = { ancla: { type: "text", label: "Nombre del apartado (para enlazarlo con #, opcional)" } };
const ESTILOS = [
    { label: "Botón dorado", value: "solido" }, { label: "Botón con borde", value: "normal" },
    { label: "Botón claro", value: "claro" }, { label: "Enlace con flecha", value: "flecha" }, { label: "Llamar a la parroquia", value: "llamar" },
];
const botones = (label = "Botones") => ({
    botones: {
        type: "array", label,
        getItemSummary: (b) => b.texto || "Botón",
        defaultItemProps: { texto: "Más información", enlace: "html/contacto.html", estilo: "normal" },
        arrayFields: {
            ...tx("texto", "Texto del botón"),
            enlace: { type: "text", label: "Enlace (por ejemplo html/misas.html o https://…)" },
            estilo: { type: "select", label: "Aspecto", options: ESTILOS },
        },
    },
});
const cabecera = () => ({ ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título"), ...adv(tx("entradilla", "Entradilla (opcional)", "textarea")) });
const boton1 = () => ({ ...tx("boton_texto", "Botón de abajo (opcional)"), boton_enlace: { type: "text", label: "Enlace del botón" } });

// ---- bloques
export function makeConfig({ render, imageField, autoPreview, advanced, help, Block }) {
    ADV = !!advanced;
    const ANCLA = ADV ? ANCLA_F : {};
    const tpl = (type) => (props) => <Block id={props.id} html={render(type, props)} />;
    const auto = (type, label, help) => ({
        label,
        fields: { aviso: { type: "custom", label: "", render: () => <p className="pst-help">{help}</p> } },
        render: () => autoPreview(type, label),
    });
    const img = (label = "Foto") => imageField(label);

    return {
        root: { fields: { ayuda: { type: "custom", label: "", render: help } } },
        categories: {
            portada: { title: "Portada", components: ["Carrusel"] },
            texto: { title: "Texto y fotos", components: ["TextoFoto", "Texto", "Columnas", "Visita", "BandaFrase", "Cita", "Llamada"] },
            tarjetas: { title: "Tarjetas, galerías y vídeo", components: ["TarjetasFoto", "TarjetasIcono", "Galeria", "Video"] },
            otros: { title: "Espacios", components: ["Separador"] },
            auto: { title: "Se actualizan solos", components: ["Horario", "Reflexion", "Agenda", "Actualidad", "Revista", "Ubicacion"] },
        },
        components: {
            Carrusel: {
                label: "Carrusel de fotos con frases",
                fields: {
                    diapositivas: {
                        type: "array", label: "Fotos del carrusel",
                        getItemSummary: (d) => d.frase || "Foto",
                        defaultItemProps: { foto: "", frase: "", posicion: 50 },
                        arrayFields: {
                            foto: img("Foto (horizontal, grande)"),
                            ...tx("frase", "Frase"),
                            ...adv({ posicion: { type: "number", label: "Encuadre vertical (0 = arriba, 50 = centro, 100 = abajo)", min: 0, max: 100 } }),
                        },
                    },
                    ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título (puede tener dos líneas)", "textarea"),
                    ...tx("subtitulo", "Texto de debajo"), ...tx("autor_frases", "Autor de las frases"), ...botones(),
                },
                defaultProps: { diapositivas: [], antetitulo: "", titulo: "Santa Teresa\nde Jesús", subtitulo: "", autor_frases: "Santa Teresa de Jesús", botones: [] },
                render: tpl("Carrusel"),
            },
            TextoFoto: {
                label: "Texto con foto",
                fields: {
                    foto: img(), ...adv(tx("foto_alt", "Descripción de la foto (para personas ciegas)")),
                    ...adv({ ...tx("sello_texto", "Sello sobre la foto: texto (opcional)"), sello_numero: { type: "text", label: "Sello: número (opcional)" } }),
                    ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título"), ...tx("texto", "Texto (deja una línea en blanco entre párrafos)", "textarea"),
                    ...adv({ cifras: {
                        type: "array", label: "Cifras destacadas (opcional)", getItemSummary: (c) => `${c.numero || ""} ${c.texto || ""}`.trim() || "Cifra",
                        defaultItemProps: { numero: "", texto: "" },
                        arrayFields: { numero: { type: "text", label: "Número (por ejemplo 1928 o +100)" }, ...tx("texto", "Qué significa") },
                    } }),
                    ...botones(), ...adv(FONDO), ...ANCLA,
                },
                defaultProps: { foto: "nuevalife.jpg", foto_alt: "", sello_texto: "", sello_numero: "", antetitulo: "", titulo: "Título del apartado", texto: "Escribe aquí el texto.", cifras: [], botones: [], fondo: "", ancla: "" },
                render: tpl("TextoFoto"),
            },
            Texto: {
                label: "Texto",
                fields: { ...cabecera(), ...tx("texto", "Texto (deja una línea en blanco entre párrafos)", "textarea"), ...botones(), ...adv(FONDO), ...ANCLA },
                defaultProps: { antetitulo: "", titulo: "Título", entradilla: "", texto: "Escribe aquí el texto.", botones: [], fondo: "", ancla: "" },
                render: tpl("Texto"),
            },
            Visita: {
                label: "Foto con pie y datos",
                fields: {
                    foto: img(), ...adv(tx("foto_alt", "Descripción de la foto (para personas ciegas)")), ...tx("pie", "Pie de foto (opcional)"),
                    ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título"), ...tx("texto", "Texto", "textarea"),
                    datos: {
                        type: "array", label: "Datos (por ejemplo Dirección, Horario…)", getItemSummary: (d) => d.etiqueta || "Dato",
                        defaultItemProps: { etiqueta: "", valor: "" }, arrayFields: { ...tx("etiqueta", "Nombre"), ...tx("valor", "Valor") },
                    },
                    ...botones(), ...adv(FONDO), ...ANCLA,
                },
                defaultProps: { foto: "vidriera.jpg", foto_alt: "", pie: "", antetitulo: "", titulo: "Título", texto: "", datos: [], botones: [], fondo: "", ancla: "" },
                render: tpl("Visita"),
            },
            BandaFrase: {
                label: "Frase sobre una foto",
                fields: { foto: img("Foto de fondo"), ...tx("frase", "Frase", "textarea"), ...tx("autor", "Autor (opcional)") },
                defaultProps: { foto: "portada2.jpg", frase: "Sólo Dios basta.", autor: "Santa Teresa de Jesús" },
                render: tpl("BandaFrase"),
            },
            Cita: {
                label: "Cita destacada",
                fields: { ...tx("frase", "Frase", "textarea"), ...tx("autor", "Autor (opcional)"), ...adv(FONDO), ...ANCLA },
                defaultProps: { frase: "Obras quiere el Señor.", autor: "Santa Teresa de Jesús", fondo: "", ancla: "" },
                render: tpl("Cita"),
            },
            Llamada: {
                label: "Recuadro con botones",
                fields: { ...tx("titulo", "Título"), ...tx("texto", "Texto (opcional)"), ...botones(), ...adv(FONDO), ...ANCLA },
                defaultProps: { titulo: "¿Te animas?", texto: "Escríbenos o pásate por el despacho parroquial.", botones: [{ texto: "Escríbenos", enlace: "html/contacto.html#escribenos", estilo: "solido" }], fondo: "", ancla: "" },
                render: tpl("Llamada"),
            },
            TarjetasFoto: {
                label: "Tarjetas con foto",
                fields: {
                    ...cabecera(),
                    tarjetas: {
                        type: "array", label: "Tarjetas", getItemSummary: (t) => t.titulo || "Tarjeta",
                        defaultItemProps: { foto: "dsc_0546.jpg", antetitulo: "", titulo: "Título", texto: "", enlace: "html/contacto.html" },
                        arrayFields: { foto: img(), ...tx("antetitulo", "Texto pequeño"), ...tx("titulo", "Título"), ...tx("texto", "Texto", "textarea"), enlace: { type: "text", label: "Enlace" } },
                    },
                    ...boton1(), ...adv(FONDO), ...ANCLA,
                },
                defaultProps: { antetitulo: "", titulo: "Título", entradilla: "", tarjetas: [], boton_texto: "", boton_enlace: "", fondo: "section-warm", ancla: "" },
                render: tpl("TarjetasFoto"),
            },
            TarjetasIcono: {
                label: "Tarjetas con icono",
                fields: {
                    ...cabecera(),
                    columnas: { type: "select", label: "Tarjetas por fila", options: [{ label: "2", value: "two" }, { label: "3", value: "three" }, { label: "4", value: "four" }, { label: "5", value: "five" }] },
                    tarjetas: {
                        type: "array", label: "Tarjetas", getItemSummary: (t) => t.titulo || "Tarjeta",
                        defaultItemProps: { icono: "caliz", titulo: "Título", texto: "", enlace: "html/contacto.html" },
                        arrayFields: { icono: { type: "select", label: "Icono", options: [] }, ...tx("titulo", "Título"), ...tx("texto", "Texto", "textarea"), enlace: { type: "text", label: "Enlace" } },
                    },
                    ...boton1(), ...adv(FONDO), ...ANCLA,
                },
                defaultProps: { antetitulo: "", titulo: "Título", entradilla: "", columnas: "three", tarjetas: [], boton_texto: "", boton_enlace: "", fondo: "", ancla: "" },
                render: tpl("TarjetasIcono"),
            },
            Galeria: {
                label: "Galería de fotos",
                fields: {
                    ...cabecera(),
                    fotos: {
                        type: "array", label: "Fotos", getItemSummary: (f) => f.alt || f.foto || "Foto",
                        defaultItemProps: { foto: "", alt: "", forma: "" },
                        arrayFields: {
                            foto: img(), ...adv(tx("alt", "Descripción de la foto")),
                            forma: { type: "select", label: "Tamaño", options: [{ label: "Normal", value: "" }, { label: "Ancha", value: "wide" }, { label: "Alta", value: "tall" }] },
                        },
                    },
                    ...boton1(), ...adv(FONDO), ...ANCLA,
                },
                defaultProps: { antetitulo: "Galería", titulo: "Fotos", entradilla: "", fotos: [], boton_texto: "", boton_enlace: "", fondo: "section-warm", ancla: "" },
                render: tpl("Galeria"),
            },
            Video: {
                label: "Vídeo de YouTube",
                fields: { video: { type: "text", label: "Enlace del vídeo de YouTube" }, ...tx("antetitulo", "Texto pequeño de arriba (opcional)"), ...tx("titulo", "Título (opcional)"), ...adv(FONDO), ...ANCLA },
                defaultProps: { video: "", antetitulo: "", titulo: "", fondo: "", ancla: "" },
                render: tpl("Video"),
            },
            Columnas: {
                label: "Columnas de texto",
                fields: {
                    ...tx("antetitulo", "Texto pequeño de arriba (opcional)"), ...tx("titulo", "Título (opcional)"),
                    columnas: {
                        type: "array", label: "Columnas", getItemSummary: (c) => c.titulo || "Columna",
                        defaultItemProps: { icono: "", titulo: "Título", texto: "Texto de la columna.", enlace: "", enlace_texto: "" },
                        arrayFields: {
                            icono: { type: "select", label: "Icono", options: [] }, ...tx("titulo", "Título"), ...tx("texto", "Texto", "textarea"),
                            enlace: { type: "text", label: "Enlace (opcional)" }, ...tx("enlace_texto", "Texto del enlace (opcional)"),
                        },
                    },
                    ...adv(FONDO), ...ANCLA,
                },
                defaultProps: { antetitulo: "", titulo: "", columnas: [
                    { icono: "", titulo: "Primera columna", texto: "Escribe aquí.", enlace: "", enlace_texto: "" },
                    { icono: "", titulo: "Segunda columna", texto: "Escribe aquí.", enlace: "", enlace_texto: "" },
                    { icono: "", titulo: "Tercera columna", texto: "Escribe aquí.", enlace: "", enlace_texto: "" }], fondo: "", ancla: "" },
                render: tpl("Columnas"),
            },
            Separador: {
                label: "Espacio entre apartados",
                fields: {
                    alto: { type: "radio", label: "Tamaño", options: [{ label: "Pequeño", value: "pequeno" }, { label: "Mediano", value: "medio" }, { label: "Grande", value: "grande" }] },
                    adorno: { type: "radio", label: "Con adorno dorado", options: [{ label: "Sí", value: true }, { label: "No", value: false }] },
                },
                defaultProps: { alto: "medio", adorno: true },
                render: tpl("Separador"),
            },
            Horario: auto("Horario", "Horario de eucaristías", "Muestra el horario de misas de la parroquia. Por ahora el horario se cambia pidiéndolo al administrador de la web."),
            Reflexion: auto("Reflexion", "Última reflexión", "Muestra sola la última homilía publicada desde el panel (Homilías y reflexiones)."),
            Agenda: auto("Agenda", "Próximos actos", "Muestra solos los tres próximos actos de la Agenda del panel."),
            Actualidad: auto("Actualidad", "Evangelio, noticias e Instagram", "El Evangelio del día y las últimas publicaciones, que se actualizan solos."),
            Revista: auto("Revista", "Revista digital", "Muestra el último número de la revista (o «Próximamente»)."),
            Ubicacion: auto("Ubicacion", "Mapa y cómo llegar", "El mapa con la dirección y cómo llegar a la parroquia."),
        },
    };
}
