define("views/CombinationsView", [
    "templates",
    "underscore",
    "views/BaseView"
], function (templates, _, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.combinations,
        "events": {
            "click .button": "change",
            "click .toggle-combinations-manager": "toggle"
        },
        "initialize": function(options) {
            this.status = options.status;
            this.selectedDisciplines = options.selectedDisciplines;
            this.listenTo(this.status, "change", this.render);
        },
        "toggle": function (e) {
            this.$("form").toggle();
            this.$(".toggle-combinations-manager").attr(
                "title",
                (this.$("form").is(":visible") ? "Esconder": "Mostrar")+" Gerenciador"
            );
            this.status.set({
                "combinations_manager_visible": this.$("form").is(":visible")
            });
            e.preventDefault();
        },
        "changeMinimumHA": function(val, maximum) {
            if (_.isNaN (val)) {
                alert("Valor inválido digitado!");
                val = null;
            }
            else if (!_.isNull(val) && val <= 0) {
                alert("Você não pode definir o minimo de horas-aula por semana como sendo igual ou menor a zero");
                val = null;
            } else if (!_.isNull(val) && maximum && maximum < val) {
                alert("Não faz sentido o número minimo de horas-aulas ser maior do que o número maximo de horas-aula");
            }
            if (val === null) {
                this.$("#minimum-ha").val("");
            }
            this.status.set({
                "minimum_ha": val
            });
        },
        "changeMaximumHA": function(val, minimum) {
            if (_.isNaN (val)) {
                alert("Valor inválido digitado!");
                val = null;
            } else if (!_.isNull(val) && val > 50) {
                alert("Você não pode criar combinações com mais de 50 horas-aula por semana!");
                val = null;
            } else if (!_.isNull(val) && minimum && minimum > val) {
                alert("Não faz sentido o número minimo de horas-aulas ser maior do que o número maximo de horas-aula");
                val = null;
            }
            if (val === null) {
                this.$("#maximum-ha").val("");
            }
            this.status.set({
                "maximum_ha": val
            });
        },
        "changeMinimumDisciplines": function(val, maximum) {
            if (_.isNaN (val)) {
                alert("Valor inválido digitado!");
                val = null;
            } else if (!_.isNull(val) && val < 1) {
                alert("Você não pode criar combinações com menos de 1 disciplina!");
                val = null;
            } else if (!_.isNull(val) && maximum && maximum < val) {
                alert("Não faz sentido o número minimo de disciplinas ser maior do que o número maximo de disciplinas");
                val = null;
            }
            if (val === null) {
                this.$("#minimum-disciplines").val("");
            }
            this.status.set({
                "minimum_disciplines": val
            });
        },
        "changeMaximumDisciplines": function(val, minimum) {
            if (_.isNaN (val)) {
                alert("Valor inválido digitado!");
                val = null;
            } else if (!_.isNull(val) && minimum && minimum > val) {
                alert("Não faz sentido o número minimo de disciplinas ser maior do que o número maximo de disciplinas");
                val = null;
            }
            if (val === null) {
                this.$("#maximum-disciplines").val("");
            }
            this.status.set({
                "maximum_disciplines": val
            });
        },
        "changePeriods": function () {
            var val = this.$(".period");
            val = _.filter(val, function(el) {
                return this.$(el).is(":checked");
            }, this);
            val = _.map(val, function(el) {
                return this.$(el).attr("name");
            }, this);
            if (val.length === 0) {
                return alert("Você precisa permitir pelo menos um periodo para processamento das combinações.");
            }
            this.status.set({
                "periods_allowed": val
            });
        },
        "changeDaysOfWeek": function () {
            var val = this.$(".dayOfWeek");
            val = _.filter(val, function(el) {
                return this.$(el).is(":checked");
            }, this);
            val = _.map(val, function(el) {
                return parseInt(this.$(el).attr("name"));
            }, this);
            if (val.length === 0) {
                return alert("Você precisa permitir pelo menos um dia da semana para processamento das combinações.");
            }
            this.status.set({
                "days_of_week_allowed": val
            });
        },
        "render": function() {
            BaseView.prototype.render.apply(this, _.toArray(arguments));
            this.$("#minimum-ha").val(this.status.get("minimum_ha"));
            this.$("#maximum-ha").val(this.status.get("maximum_ha"));
            this.$("#minimum-disciplines").val(this.status.get("minimum_disciplines"));
            this.$("#maximum-disciplines").val(this.status.get("maximum_disciplines"));
            var periods = this.status.get("periods_allowed");
            var val = this.$(".period");
            var c;
            val.prop("checked", false);
            val = _.filter(val, function(el) {
                return periods.indexOf(this.$(el).attr("name")) !== -1;
            }, this);
            for(c=0; c<val.length; c++) {
                this.$(val[c]).prop("checked", true);
            }
            var daysOfWeek = this.status.get("days_of_week_allowed");
            val = this.$(".dayOfWeek");
            val.prop("checked", false);
            val = _.filter(val, function(el) {
                return daysOfWeek.indexOf(parseInt(this.$(el).attr("name"))) !== -1;
            }, this);
            for(c=0; c<val.length; c++) {
                this.$(val[c]).prop("checked", true);
            }
            if (this.$("form").is(":visible") !== !!this.status.get("combinations_manager_visible")) {
                this.$(".toggle-combinations-manager").click();
            }
        },
        "getValueFrom": function(selector) {
            var val = this.$(selector).val();
            return _.isEmpty(val) ? null : parseInt(val);
        },
        "change": function(e) {
            var minimumHA= this.getValueFrom("#minimum-ha");
            var maximumHA = this.getValueFrom("#maximum-ha");
            var minimumDisciplines = this.getValueFrom("#minimum-disciplines");
            var maximumDisciplines = this.getValueFrom("#maximum-disciplines");
            this.changeMinimumHA(minimumHA, maximumHA);
            this.changeMaximumHA(maximumHA, minimumHA);
            this.changeMinimumDisciplines(minimumDisciplines, maximumDisciplines);
            this.changeMaximumDisciplines(maximumDisciplines, minimumDisciplines);
            this.changePeriods();
            this.changeDaysOfWeek();
            this.selectedDisciplines.updateCombinations();
            e.preventDefault();
        }
    });
});