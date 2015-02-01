define("views/SelectedTeamView", [
    "templates",
    "jquery",
    "underscore",
    "views/BaseView"
], function (templates, $, _, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.selectedTeam,
        "tagName": "tr",
        "events": {
            "mouseover": "focusTeam",
            "mouseout": "unfocusTeam",
            "click .selectedTeam": "updateSelectedTeam",
            "change model": "render"
        },
        "initialize": function (options) {
            BaseView.prototype.initialize.apply(this, [options]);
            this.selectedDisciplines = options.selectedDisciplines;
        },
        "focusTeam": function () {
            if (!this.model || this.model.disposed) {
                return;
            }
            if (this.model.discipline.team === this.model) {
                this.model.discipline.hoveredTeam = null;
                return;
            }
            this.model.discipline.hoveredTeam = this.model;
            this.selectedDisciplines.trigger("change:combination");
        },
        "unfocusTeam": function () {
            if (!this.model || this.model.disposed) {
                return;
            }
            this.model.discipline.hoveredTeam = null;
            this.selectedDisciplines.trigger("change:combination");
        },
        "updateSelectedTeam": function (e) {
            if (!this.model || this.model.disposed) {
                return;
            }
            this.model.set({
                "_selected": this.$(e.currentTarget).is(":checked")
            });
            this.selectedDisciplines.updateCombinations();
            this.selectedDisciplines.trigger("change:combination");
            this.render();
        },
        "getTemplateData": function () {
            return {
                "team": this.model
            };
        },
        "render": function () {
            BaseView.prototype.render.apply(this, []);
            if (!this.model || this.model.disposed) {
                return;
            }
            var el = this.$("td");
            el.css({
                "background-color": this.model.discipline.get("_color"),
                "opacity": this.model.get("_selected") ? 1 : 0.5,
                "border-top": this.model.startGrouping ? "2px #000000 solid" : "",
                "border-bottom": this.model.endGrouping ? "2px #000000 solid" : ""
            });
        },
        "dispose": function () {
            var view = this;
            this.$el.animate({
                "opacity": 0
            }, 400, function () {
                BaseView.prototype.dispose.apply(view, []);
            });
        }
    });
});