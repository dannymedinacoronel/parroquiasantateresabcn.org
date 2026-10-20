/* Calendario litúrgico (rito romano) calculado en el navegador, sin servicios externos.
   PSTLiturgia.dia(fecha, idioma) -> "Martes de la XXIX semana del Tiempo Ordinario"
   Rellena solo los elementos con [data-liturgia] y [data-hoy] de la página. */
(function () {
    var DAY = 864e5;

    function utc(y, m, d) { return Date.UTC(y, m, d); }
    function easter(y) { // algoritmo de Meeus / Butcher
        var a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4,
            f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3),
            h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4,
            l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451),
            month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
        return utc(y, month - 1, day);
    }
    function dow(t) { return new Date(t).getUTCDay(); }
    function advent1(y) { var x = utc(y, 11, 25); return x - ((dow(x) || 7) + 21) * DAY; }
    function baptism(y) { var x = utc(y, 0, 6); return x + (7 - dow(x)) * DAY; }
    function roman(n) {
        var r = "", v = [[10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];
        for (var i = 0; i < v.length; i++) while (n >= v[i][0]) { r += v[i][1]; n -= v[i][0]; }
        return r;
    }
    function ordEn(n) {
        var s = (n % 100 >= 11 && n % 100 <= 13) ? "th" : ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th");
        return n + s;
    }

    var L = {
        es: {
            days: ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
            seasons: { adv: "de Adviento", cua: "de Cuaresma", pas: "de Pascua", ord: "del Tiempo Ordinario" },
            sunday: function (n, s) { return roman(n) + " domingo " + this.seasons[s]; },
            week: function (d, n, s) { return d + " de la " + roman(n) + " semana " + this.seasons[s]; },
            navidad: "Tiempo de Navidad", natividad: "Natividad del Señor", epifania: "Epifanía del Señor",
            bautismo: "Bautismo del Señor", ceniza: "Miércoles de Ceniza", trasCeniza: function (d) { return d + " después de Ceniza"; },
            ramos: "Domingo de Ramos", santo: function (d) { return d + " Santo"; }, resurreccion: "Domingo de Resurrección",
            octava: function (d) { return d + " de la Octava de Pascua"; }, pentecostes: "Domingo de Pentecostés",
            rey: "Jesucristo, Rey del Universo"
        },
        ca: {
            days: ["Diumenge", "Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte"],
            seasons: { adv: "d'Advent", cua: "de Quaresma", pas: "de Pasqua", ord: "de durant l'any" },
            sunday: function (n, s) { return roman(n) + " diumenge " + this.seasons[s]; },
            week: function (d, n, s) { return d + " de la " + roman(n) + " setmana " + this.seasons[s]; },
            navidad: "Temps de Nadal", natividad: "Nativitat del Senyor", epifania: "Epifania del Senyor",
            bautismo: "Baptisme del Senyor", ceniza: "Dimecres de Cendra", trasCeniza: function (d) { return d + " després de Cendra"; },
            ramos: "Diumenge de Rams", santo: function (d) { return d + " Sant"; }, resurreccion: "Diumenge de Pasqua",
            octava: function (d) { return d + " de l'Octava de Pasqua"; }, pentecostes: "Diumenge de Pentecosta",
            rey: "Jesucrist, Rei de tot el món"
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            seasons: { adv: "of Advent", cua: "of Lent", pas: "of Easter", ord: "in Ordinary Time" },
            sunday: function (n, s) { return ordEn(n) + " Sunday " + this.seasons[s]; },
            week: function (d, n, s) { return d + " of the " + ordEn(n) + " Week " + this.seasons[s]; },
            navidad: "Christmas Time", natividad: "The Nativity of the Lord", epifania: "The Epiphany of the Lord",
            bautismo: "The Baptism of the Lord", ceniza: "Ash Wednesday", trasCeniza: function (d) { return d + " after Ash Wednesday"; },
            ramos: "Palm Sunday", santo: function (d) { return d === "Thursday" ? "Holy Thursday" : d === "Friday" ? "Good Friday" : d === "Saturday" ? "Holy Saturday" : d + " of Holy Week"; },
            resurreccion: "Easter Sunday", octava: function (d) { return d + " within the Octave of Easter"; },
            pentecostes: "Pentecost Sunday", rey: "Our Lord Jesus Christ, King of the Universe"
        }
    };

    function dia(fecha, lang) {
        var t = L[lang] || L.es;
        var f = fecha || new Date();
        var y = f.getFullYear(), d = utc(y, f.getMonth(), f.getDate()), wd = dow(d), dn = t.days[wd];
        var E = easter(y), ash = E - 46 * DAY, palm = E - 7 * DAY, pent = E + 49 * DAY,
            adv = advent1(y), bap = baptism(y), xmas = utc(y, 11, 25), epi = utc(y, 0, 6);
        var w = function (a) { return Math.floor((d - a) / (7 * DAY)) + 1; };

        if (d === xmas) return t.natividad;
        if (d > xmas) return t.navidad;
        if (d >= adv) return wd === 0 ? t.sunday(w(adv), "adv") : t.week(dn, w(adv), "adv");
        if (d === epi) return t.epifania;
        if (d === bap) return t.bautismo;
        if (d < bap) return t.navidad;
        if (d < ash) {
            var n = Math.floor((d - bap) / (7 * DAY)) + 1;
            return wd === 0 ? t.sunday(n, "ord") : t.week(dn, n, "ord");
        }
        if (d === ash) return t.ceniza;
        if (d < ash + 4 * DAY) return t.trasCeniza(dn);
        if (d < palm) return wd === 0 ? t.sunday(w(ash + 4 * DAY), "cua") : t.week(dn, w(ash + 4 * DAY), "cua");
        if (d === palm) return t.ramos;
        if (d < E) return t.santo(dn);
        if (d === E) return t.resurreccion;
        if (d < E + 7 * DAY) return t.octava(dn);
        if (d < pent) return wd === 0 ? t.sunday(w(E), "pas") : t.week(dn, w(E), "pas");
        if (d === pent) return t.pentecostes;
        var o = 34 - Math.floor((adv - d - DAY) / (7 * DAY));
        if (d === adv - 7 * DAY) return t.rey;
        return wd === 0 ? t.sunday(o, "ord") : t.week(dn, o, "ord");
    }

    window.PSTLiturgia = { dia: dia };

    function fill() {
        var lang = (document.documentElement.lang || "es").slice(0, 2);
        var locale = { es: "es-ES", ca: "ca-ES", en: "en-GB" }[lang] || "es-ES";
        var hoy = new Date();
        document.querySelectorAll("[data-liturgia]").forEach(function (el) { el.textContent = dia(hoy, lang); });
        document.querySelectorAll("[data-hoy]").forEach(function (el) {
            el.textContent = hoy.toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
        });
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fill); else fill();
})();
