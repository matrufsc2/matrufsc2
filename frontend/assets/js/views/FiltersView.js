define("views/FiltersView", [
	"underscore",
    "jquery",
	"templates",
	"views/BaseView",
    "views/SelectView",
    "views/AutoCompleteView",
	"models/Discipline",
    "models/Team",
    "foundation-tooltip"
], function(_, $, templates, BaseView, SelectView, AutoCompleteView, Discipline, Team){
	"use strict";
	return BaseView.extend({
        "template": templates.filters,
        "listen": {
            "render": "renderFilters",
            "addedToDOM": "applyFoundation"
        },
        "initialize": function (options) {
            _.extend(this, _.pick(options, ["selectedDisciplines", "semesters", "campi", "status"]));
        },
        "renderSemester": function () {
            // Process Semesters..
            var view = new SelectView({
                "el": this.$("#semester"),
                "collection": this.semesters,
                "statusKey": "semester",
                "status": this.status,
                "labelName": "name"
            });
            this.subview("semester", view);
        },
        "renderCampus": function () {
            // Process Semesters..
            var view = new SelectView({
                "el": this.$("#campus"),
                "collection": this.campi,
                "statusKey": "campus",
                "status": this.status,
                "labelName": "name"
            });
            this.subview("campus", view);
        },
        "renderDisciplines": function () {
            var onGetDiscipline = function (discipline) {
                return discipline.code + " - " + discipline.name;
            };
            var parentView = this;
            var view = new AutoCompleteView({
                "url": function() {
                    return Discipline.prototype.urlRoot + "?page=%(page)d&limit=%(pageSize)d&q=%(searchString)s&campus=" + parentView.status.get("campus");
                },
                "getFormattedString": onGetDiscipline,
                "formatDidYouMean": "Você quis dizer:",
                "prepareResults": function(results, term) {
                    var newResults = [];
                    if (results[0] && results[0]._custom) {
                        results = results.splice(1);
                    }
                    var suggestionsAnswer = _.all(results, function(result) {
                        return !result.id;
                    });
                    for(var c=0; c<results.length; ++c) {
                        if (!results[c].id) {
                            newResults.push(results[c]);
                            continue;
                        }
                        if (parentView.selectedDisciplines.get(results[c].id)) {
                            continue;
                        }
                        results[c]._custom = false;
                        results[c].text = onGetDiscipline(results[c]);
                        newResults.push(results[c]);
                    }
                    if (term.length === 0 || term.length >= 30) {
                        return {
                            "results": newResults,
                            "selectedItem": suggestionsAnswer ? 1 : 0
                        };
                    }
                    return {
                        "results": [{
                            "text": "Criar atividade extra: <b>" + $("<span>"+term+"</span>").text() + "</b>",
                            "id": term.toUpperCase().substr(0, 7),
                            "code": term.toUpperCase().substr(0, 7),
                            "name": term,
                            "_custom": true,
                            "highlight": false
                        }].concat(newResults),
                        "selectedItem": newResults.length > 0 ? (suggestionsAnswer ? 0 : 1) : 0
                    };
                },
                "pageable": true,
                "el": this.$("#discipline-field"),
                "formatNoMatches": "Nenhum resultado encontrado :(",
                "formatLoading": "Carregando, aguarde...",
                "processSelectedItem": function(discipline) {
                    var model;
                    if (discipline._custom) {
                        model = parentView.selectedDisciplines.get(discipline.id);
                        var new_model = false;
                        if (model) {
                            return alert("Você não pode adicionar uma disciplina com os mesmos primeiros 7 caracteres que outra já selecionada");
                        } else {
                            model = new Discipline(discipline);
                            var team = new Team({
                                "id": "0001",
                                "code": "0001",
                                "vacancies_offered": 1,
                                "vacancies_filled": 0,
                                "_selected": true,
                                "teachers": [{
                                    "name": "Você"
                                }],
                                "schedules": []
                            });
                            team.discipline = model;
                            model.teams.add(team);
                            new_model = true;
                        }
                    } else {
                        model = new Discipline(discipline);
                        model.campus = parentView.status.get("campus");
                    }
                    model.select().then(function () {
                        parentView.selectedDisciplines.add(model);
                    });
                }
            });
            this.subview("disciplines", view);
        },
        "renderFilters": function () {
            this.applyFoundation();
            this.renderSemester();
            this.renderCampus();
            this.renderDisciplines();
        }
    });
});