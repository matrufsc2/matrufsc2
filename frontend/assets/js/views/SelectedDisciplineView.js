define("views/SelectedDisciplineView", [
    "templates",
    "jquery",
    "underscore",
    "views/BaseView",
    "foundation-tooltip",
    "foundation-dropdown"
], function (templates, $, _, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.selectedDiscipline,
        "tagName": "tr",
        "events": {
            "click .icon-delete": "unselect",
            "click .selectedDiscipline": "updateTeams",
            "click .icon-up": "moveUp",
            "click .icon-down": "moveDown",
            "click .icon-edit": "edit",
            "click .icon-ok": "save",
            "click .discipline-name": "editName",
            "click td:lt(4)": "select"
        },
        "initialize": function (options) {
            this.status = options.status;
            this.blinking = false;
            this.listenTo(this.model.teams, "syncStateChange", this.render);
        },
        "editName": function (e) {
            e.preventDefault();
            var valid = false;
            var name;
            while (valid === false) {
                name = prompt("Informe o nome que você deseja dar a essa disciplina:");
                if (name) {
                    valid = name.length > 0 && name.length < 30;
                    if (!valid) {
                        alert("Informe um codigo valido! (entre 1 e 29 caracteres)");
                    }
                } else {
                    return;
                }
            }
            this.model.set({
                "id": name.toUpperCase().substr(0, 7),
                "code": name.toUpperCase().substr(0, 7),
                "name": name
            });
            this.status.set({
                "discipline": name.toUpperCase()
            });
            this.render();
        },
        "canEdit": function () {
            return this.model.get("_custom") === true;
        },
        "isEditing": function () {
            return this.canEdit() && this.model.id === this.status.get("discipline") &&
                this.status.get("editing") === true;
        },
        "getTemplateData": function () {
            return {
                "discipline": this.model,
                "can_edit": this.canEdit(),
                "is_editing": this.isEditing()
            };
        },
        "edit": function (e) {
            if (!this.canEdit()) {
                e.preventDefault();
                return alert("Nao e possivel editar esta disciplina pois ela nao é personalizada!");
            }
            this.select(e);
            this.model.teams.each(function (team) {
                // Descompact the schedules for each team to allow easy editing
                team.schedules.descompact();
            });
            this.status.set({
                "editing": true
            });
            this.render();
            e.preventDefault();
        },
        "save": function (e) {
            if (!this.isEditing()) {
                e.preventDefault();
                return alert("Nao e possivel editar esta disciplina pois ela nao está sendo edidtada! (e isso parece um bug)");
            }
            this.status.set({
                "editing": false
            });
            this.model.teams.each(function (team) {
                // Compact the schedules for each team to avoid inneficient space
                team.schedules.compact();
            });
            this.model.collection.updateCombinations();
            this.model.collection.trigger("change:combination");
            this.render();
        },
        "select": function (e) {
            e.stopPropagation();
            if (this.status.get("editing") && this.status.get("discipline") !== this.model.id) {
                return alert("Você não selecionar outra disciplina enquanto está no modo de edição de disciplinas personalizadas");
            }
            this.status.set({
                "discipline": this.model.id
            });
            this.model.collection.updateCombinations();
            this.model.collection.trigger("change:combination");
            this.render();
            e.preventDefault();
        },
        "unselect": function (e) {
            e.stopPropagation();
            if (this.status.get("editing") && this.status.get("discipline") !== this.model.id) {
                return alert("Você não deselecionar outra disciplina enquanto está no modo de edição de disciplinas personalizadas");
            }
            this.model.unselect();
            this.status.set({
                "discipline": null,
                "editing": false
            });
            this.render();
            e.preventDefault();
        },
        "updateTeams": function (e) {
            e.stopPropagation();
            if (this.status.get("editing") && this.status.get("discipline") !== this.model.id) {
                e.preventDefault();
                return alert("Você não desmarcar as turmas de outra disciplina enquanto está no modo de edição de disciplinas personalizadas");
            }
            var isEnabled = this.$(e.currentTarget).is(":checked");
            this.model.teams.each(function (team) {
                team.set({
                    "_selected": isEnabled
                });
            });
            this.model.collection.updateCombinations();
            this.model.collection.trigger("change:combination");
            this.render();
            this.status.trigger("change:discipline");
        },
        "moveUp": function (e) {
            this.model.moveUp();
            e.preventDefault();
        },
        "moveDown": function (e) {
            this.model.moveDown();
            e.preventDefault();
        },
        "render": function () {
            BaseView.prototype.render.call(this);
            if (this.model.has("_title") && this.blinking === false) {
                this.blinking = true;
                _.delay(function blink(view, status) {
                    if (view.disposed || !view.model) {
                        return;
                    }
                    if (!view.model.has("_title")) {
                        view.$(".title").css("opacity", 1);
                        view.blinking = false;
                        return;
                    }
                    view.$(".title").animate({
                        "opacity": status ? 1 : 0.5
                    }, 400, "swing", function () {
                        _.delay(blink, 500, view, !status);
                    });
                }, 500, this, false);
            }
            var originalColor = this.model.get("_color").substr(1);
            var color = "rgba(" +
                parseInt(originalColor.substr(0, 2), 16) + "," +
                parseInt(originalColor.substr(2, 2), 16) + "," +
                parseInt(originalColor.substr(4, 2), 16) + "," +
                (this.model.isDisciplineEnabled() ? 1 : 0.5) +
                ")";
            this.$el.css("background-color", color);
        }
    });
});