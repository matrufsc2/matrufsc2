define("models/HistoryItem", ["models/BaseModel"], function (BaseModel) {
    "use strict";
    var SECOND = 1000,
        MINUTE = 60 * SECOND,
        HOUR = 60 * MINUTE,
        DAY = 24 * HOUR,
        WEEK = 7 * DAY,
        YEAR = DAY * 365,
        MONTH = YEAR / 12,
        WEEKDAYS = "domingo_segunda-feira_terça-feira_quarta-feira_quinta-feira_sexta-feira_sábado".split("_"),
        MONTHS = "janeiro_fevereiro_março_abril_maio_junho_julho_agosto_setembro_outubro_novembro_dezembro".split("_");
    var formats = [
        [0.7 * MINUTE, 'agora mesmo'],
        [1.5 * MINUTE, 'um minuto atrás'],
        [60 * MINUTE, 'minutos atrás', MINUTE],
        [1.5 * HOUR, 'uma hora atrás'],
        [DAY, 'horas atrás', HOUR],
        [2 * DAY, 'ontem'],
        [7 * DAY, 'dias atrás', DAY],
        [1.5 * WEEK, 'uma semana atrás'],
        [MONTH, 'semanas atrás', WEEK],
        [1.5 * MONTH, 'um mês atrás'],
        [YEAR, 'meses atrás', MONTH],
        [1.5 * YEAR, 'um ano atrás'],
        [Number.MAX_VALUE, 'anos atrás', YEAR]
    ];

    function relativeDate(input, reference) {
        if(!reference) {
            reference = new Date();
        }
        if (reference instanceof Date) {
            reference = reference.getTime();
        }
        if (input instanceof Date) {
            input = input.getTime();
        }
        var delta = reference - input,
            format, i, len;
        for (i = 0, len = formats.length; i < len; i++) {
            format = formats[i];
            if (delta < format[0]) {
                return format[2] === undefined ? format[1] : Math.round(delta / format[2]) + ' ' + format[1];
            }
        }
    }

    return BaseModel.extend({
        "defaults": function () {
            return {
                "id": 0,
                "data": {}
            };
        },
        "getDate": function () {
            return new Date(this.id);
        },
        "getFormattedRelativeDate": function () {
            return relativeDate(this.getDate(), new Date());
        },
        "getFormattedDate": function () {
            var old = this.getDate();
            var day = "0"+ old.getDate();
            var hours = "0" + old.getHours();
            var minutes = "0" + old.getMinutes();
            var seconds = "0" + old.getSeconds();
            return WEEKDAYS[old.getDay()]+", "+day.substr(-2, 2)+" de "+MONTHS[old.getMonth()]+" de "+
                old.getFullYear()+" às "+hours.substr(-2, 2)+":"+minutes.substr(-2, 2)+":"+seconds.substr(-2, 2);
        }
    });
});