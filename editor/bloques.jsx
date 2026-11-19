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

export const TEMPLATES = { Carrusel, TextoFoto, BandaFrase, TarjetasFoto, TarjetasIcono, Galeria, Visita, Texto, Cita, Llamada };

// ---- campos reutilizables
// texto en castellano + traducción opcional (català / English) debajo
let ADV = false;   // «Más opciones»: traducciones y campos técnicos
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
const cabecera = () => ({ ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título"), ...tx("entradilla", "Entradilla (opcional)", "textarea") });
const boton1 = () => ({ ...tx("boton_texto", "Botón de abajo (opcional)"), boton_enlace: { type: "text", label: "Enlace del botón" } });

// ---- bloques
export function makeConfig({ render, imageField, autoPreview, advanced, help }) {
    ADV = !!advanced;
    const ANCLA = ADV ? ANCLA_F : {};
    const tpl = (type) => (props) => <div className="pst-block" dangerouslySetInnerHTML={{ __html: render(type, props) }} />;
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
            texto: { title: "Texto y fotos", components: ["TextoFoto", "Texto", "Visita", "BandaFrase", "Cita", "Llamada"] },
            tarjetas: { title: "Tarjetas y galerías", components: ["TarjetasFoto", "TarjetasIcono", "Galeria"] },
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
                            posicion: { type: "number", label: "Encuadre vertical (0 = arriba, 50 = centro, 100 = abajo)", min: 0, max: 100 },
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
                    foto: img(), ...tx("foto_alt", "Descripción de la foto (para personas ciegas)"),
                    ...tx("sello_texto", "Sello sobre la foto: texto (opcional)"), sello_numero: { type: "text", label: "Sello: número (opcional)" },
                    ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título"), ...tx("texto", "Texto (deja una línea en blanco entre párrafos)", "textarea"),
                    cifras: {
                        type: "array", label: "Cifras destacadas (opcional)", getItemSummary: (c) => `${c.numero || ""} ${c.texto || ""}`.trim() || "Cifra",
                        defaultItemProps: { numero: "", texto: "" },
                        arrayFields: { numero: { type: "text", label: "Número (por ejemplo 1928 o +100)" }, ...tx("texto", "Qué significa") },
                    },
                    ...botones(), ...FONDO, ...ANCLA,
                },
                defaultProps: { foto: "nuevalife.jpg", foto_alt: "", sello_texto: "", sello_numero: "", antetitulo: "", titulo: "Título del apartado", texto: "Escribe aquí el texto.", cifras: [], botones: [], fondo: "", ancla: "" },
                render: tpl("TextoFoto"),
            },
            Texto: {
                label: "Texto",
                fields: { ...cabecera(), ...tx("texto", "Texto (deja una línea en blanco entre párrafos)", "textarea"), ...botones(), ...FONDO, ...ANCLA },
                defaultProps: { antetitulo: "", titulo: "Título", entradilla: "", texto: "Escribe aquí el texto.", botones: [], fondo: "", ancla: "" },
                render: tpl("Texto"),
            },
            Visita: {
                label: "Foto con pie y datos",
                fields: {
                    foto: img(), ...tx("foto_alt", "Descripción de la foto (para personas ciegas)"), ...tx("pie", "Pie de foto (opcional)"),
                    ...tx("antetitulo", "Texto pequeño de arriba"), ...tx("titulo", "Título"), ...tx("texto", "Texto", "textarea"),
                    datos: {
                        type: "array", label: "Datos (por ejemplo Dirección, Horario…)", getItemSummary: (d) => d.etiqueta || "Dato",
                        defaultItemProps: { etiqueta: "", valor: "" }, arrayFields: { ...tx("etiqueta", "Nombre"), ...tx("valor", "Valor") },
                    },
                    ...botones(), ...FONDO, ...ANCLA,
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
                fields: { ...tx("frase", "Frase", "textarea"), ...tx("autor", "Autor (opcional)"), ...FONDO, ...ANCLA },
                defaultProps: { frase: "Obras quiere el Señor.", autor: "Santa Teresa de Jesús", fondo: "", ancla: "" },
                render: tpl("Cita"),
            },
            Llamada: {
                label: "Recuadro con botones",
                fields: { ...tx("titulo", "Título"), ...tx("texto", "Texto (opcional)"), ...botones(), ...FONDO, ...ANCLA },
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
                    ...boton1(), ...FONDO, ...ANCLA,
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
                    ...boton1(), ...FONDO, ...ANCLA,
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
                            foto: img(), ...tx("alt", "Descripción de la foto"),
                            forma: { type: "select", label: "Tamaño", options: [{ label: "Normal", value: "" }, { label: "Ancha", value: "wide" }, { label: "Alta", value: "tall" }] },
                        },
                    },
                    ...boton1(), ...FONDO, ...ANCLA,
                },
                defaultProps: { antetitulo: "Galería", titulo: "Fotos", entradilla: "", fotos: [], boton_texto: "", boton_enlace: "", fondo: "section-warm", ancla: "" },
                render: tpl("Galeria"),
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
