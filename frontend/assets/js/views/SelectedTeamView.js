define("views/SelectedTeamView", [
    "templates",
    "jquery",
    "underscore",
    "views/BaseView",
    "foundation-tooltip"
], function (templates, $, _, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.selectedTeam,
        "tagName": "tr",
        "events": {
            "mouseover": "focusTeam",
            "mouseout": "unfocusTeam",
            "click .removeTeam": "removeTeam",
            "click .deselectAnothers": "deselectAnothers",
            "click .selectedTeam": "updateSelectedTeam",
            "click .icon-edit": "editTeam",
            "click .icon-ok": "saveTeam"
        },
        "listen": {
            "change model": "render"
        },
        "initialize": function (options) {
            BaseView.prototype.initialize.apply(this, [options]);
            this.selectedDisciplines = options.selectedDisciplines;
            this.discipline = options.discipline;
            this.status = options.status;
            this.isEditingDiscipline = options.isEditingDiscipline;
            this.isEditingTeam = options.isEditingTeam;
        },
        "removeTeam": function (e) {
            e.preventDefault();
            if (!this.isEditingDiscipline) {
                return alert("Impossivel apagar turma de disciplina que não está sendo editada");
            }
            if (!confirm("Você tem certeza que deseja apagar a turma " + this.model.get("code") + "?")) {
                return false;
            }
            if (this.discipline.team && this.discipline.team.id === this.model.id) {
                this.discipline.team = null;
            }
            this.discipline.teams.remove(this.model);
            this.status.trigger("change:discipline");
        },
        "deselectAnothers": function (e) {
            e.preventDefault();
            this.discipline.teams.each(function (team) {
                team.set({
                    "_selected": team.id === this.model.id
                });
            }, this);
            this.discipline.collection.updateCombinations();
            this.discipline.collection.trigger("change:combination");
        },
        "focusTeam": function () {
            if (!this.model || this.model.disposed) {
                return;
            }
            if (this.model.discipline.team === this.model) {
                this.model.discipline.hoveredTeam = null;
                return true;
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
        "editTeam": function (e) {
            e.preventDefault();
            if (!this.isEditingDiscipline) {
                return alert("Impossivel editar turma pertencente a disciplina que não está sendo editada");
            }
            this.discipline.team = this.model;
            this.isEditingTeam = true;
            this.status.trigger("change:discipline");
        },
        "saveTeam": function (e) {
            e.preventDefault();
            if (!this.isEditingTeam) {
                return alert("Impossivel salvar turma que não está sendo editada");
            }

            if (this.discipline.teams.length === 1) {
                this.status.set({
                    "editing": false
                });
                this.discipline.teams.each(function (team) {
                    // Compact the schedules for each team to avoid inneficient space
                    team.schedules.compact();
                });
                this.discipline.collection.updateCombinations();
                this.discipline.collection.trigger("change:combination");
            } else {
                this.discipline.team = null;
            }
            this.isEditingTeam = false;
            this.render();
        },
        "updateSelectedTeam": function (e) {
            if (!this.model || this.model.disposed) {
                return;
            }
            if (this.model.discipline.get("_custom")) {
                this.model.discipline.team = this.model;
                this.selectedDisciplines.trigger("change:combination");
            } else {
                this.model.set({
                    "_selected": this.$(e.currentTarget).is(":checked")
                });
                this.selectedDisciplines.updateCombinations();
                this.render();
            }
        },
        "getTemplateData": function () {
            return {
                "team": this.model,
                "is_editing_discipline": this.isEditingDiscipline,
                "is_editing_team": this.isEditingTeam
            };
        },
        "render": function () {
            BaseView.prototype.render.call(this);
            if (!this.model || this.model.disposed) {
                return;
            }
            var el = this.$("td");
            var originalColor = this.model.discipline.get("_color").substr(1);
            var color = "rgba(" +
                parseInt(originalColor.substr(0, 2), 16) + "," +
                parseInt(originalColor.substr(2, 2), 16) + "," +
                parseInt(originalColor.substr(4, 2), 16) + "," +
                (this.model.get("_selected") ? 1 : 0.5) +
                ")";
            el.css({
                "background-color": color,
                "border-top": this.model.startGrouping ? "2px #000000 solid" : "",
                "border-bottom": this.model.endGrouping ? "2px #000000 solid" : ""
            });
            this.applyFoundation();
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