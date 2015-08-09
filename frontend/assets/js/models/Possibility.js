define("models/Possibility", [
    "models/BaseModel",
    "models/Discipline",
    "models/Team",
    "models/Campus",
    "underscore",
    "es6-promise"
], function (BaseModel, Discipline, Team, Campus, _) {
    "use strict";
    function purify(id, type) {
        return (id || "").replace("matrufsc2-" + type + "-", "");
    }

    function unpurify(id, type) {
        return "matrufsc2-" + type + "-" + purify(id, type);
    }

    return BaseModel.extend({
        "defaults": {
            "id": null,
            "selectedDisciplines": [],
            "semester": null,
            "campus": null,
            "teams": [],
            "discipline": null,
            "selectedCombination": 0
        },
        "loadPossibility": function (status, selectedDisciplines) {
            var statusSession = this.toJSON();
            selectedDisciplines.reset();
            // Adds the selected discipline as a response to the user
            return new Promise(function (resolve, reject) {
                if (status.get("editing")) {
                    return reject("Saia do modo de edição antes de carregar outro plano");
                }
                status.set({
                    "discipline": null
                });
                status.once("change:semester", function () {
                    status.once("change:campus", function () {
                        if (!statusSession.selectedDisciplines.length) {
                            return resolve();
                        }
                        var selectedDisciplinesModels = [];
                        for (var c = 0; c < statusSession.selectedDisciplines.length; c++) {
                            var sd = statusSession.selectedDisciplines[c];
                            var model;
                            if (sd._custom) {
                                model = new Discipline(sd);
                            } else {
                                model = new Discipline({
                                    "id": unpurify(sd.id, "discipline")
                                });
                                model.set({
                                    "name": "Carregando.."
                                });
                            }
                            model.campus = new Campus({
                                "id": unpurify(statusSession.campus, 'campus')
                            });
                            selectedDisciplinesModels.push(model);
                        }
                        selectedDisciplines.add(selectedDisciplinesModels);
                        var processSelectedDiscipline = _.bind(function (discipline, selectedDiscipline) {
                            var promiseTemp;
                            if (selectedDiscipline._custom) {
                                promiseTemp = discipline.select();
                            } else {
                                promiseTemp = discipline.fetch().then(function () {
                                    selectedDisciplines.updateCombinations(statusSession.selectedCombination);
                                    return discipline.select();
                                });
                            }
                            return promiseTemp.then(_.bind(function () {
                                return Promise.all(
                                    _.map(_.where(statusSession.teams, {
                                        "discipline": selectedDiscipline.id
                                    }), function (teamOriginal) {
                                        var team;
                                        if (discipline.get("_custom")) {
                                            team = new Team(teamOriginal);
                                            team.discipline = discipline;
                                            discipline.teams.add(team);
                                        } else {
                                            team = discipline.teams.get(unpurify(teamOriginal.id, "team"));
                                        }
                                        if (team) {
                                            team.set({"_selected": teamOriginal._selected});
                                            return Promise.resolve();
                                        } else {
                                            return reject("Foram encontradas turmas que nao existem mais na disciplina " + discipline.get("name"));
                                        }
                                    }, this)
                                ).then(function () {
                                        // We need to trigger an update in combinations to update the UI too :D
                                        selectedDisciplines.updateCombinations(statusSession.selectedCombination);
                                    });
                            }, this));
                        }, this);
                        Promise.resolve(0).then(function process(c) {
                            var tempPromise = processSelectedDiscipline(
                                selectedDisciplinesModels[c],
                                statusSession.selectedDisciplines[c]
                            );
                            if (statusSession.selectedDisciplines.length > c) {
                                tempPromise = tempPromise.then(function () {
                                    return process(c + 1);
                                });
                            }
                            return tempPromise;
                        }).then(function () {
                            return selectedDisciplines.updateCombinations(
                                statusSession.selectedCombination
                            );
                        }).then(function () {
                            if (statusSession.discipline) {
                                status.set({
                                    "discipline": unpurify(statusSession.discipline, "discipline")
                                });
                            }
                            resolve();
                        }, reject);
                    });
                    if (!statusSession.campus) {
                        return resolve();
                    }
                    var campus = unpurify(statusSession.campus, "campus");
                    if (status.get("campus") !== campus) {
                        status.set({
                            "campus": campus
                        });
                    } else {
                        status.trigger("change:campus");
                    }

                }, this);
                if (!statusSession.semester) {
                    return resolve();
                }
                var semester = unpurify(statusSession.semester, "semester");
                if (semester !== status.get("semester")) {
                    status.set({
                        "semester": semester
                    });
                    status.trigger("change:semester");
                } else {
                    status.trigger("change:semester");
                }
                var newFields = _.pick(statusSession, [
                    "minimum_disciplines",
                    "maximum_disciplines",
                    "minimum_ha",
                    "maximum_ha",
                    "days_of_week_allowed",
                    "periods_allowed"
                ]);
                if (!_.isEmpty(newFields)) {
                    status.set({
                        "minimum_disciplines": statusSession.minimum_disciplines,
                        "maximum_disciplines": statusSession.maximum_disciplines,
                        "minimum_ha": statusSession.minimum_ha,
                        "maximum_ha": statusSession.maximum_ha,
                        "days_of_week_allowed": statusSession.days_of_week_allowed,
                        "periods_allowed": statusSession.periods_allowed
                    });
                }
            });
        },
        "savePossibility": function (status, selectedDisciplines, silent) {
            if (this.disposed || !status || !selectedDisciplines) {
                return;
            }
            var data = {};
            data.minimum_disciplines = status.get("minimum_disciplines");
            data.maximum_disciplines = status.get("maximum_disciplines");
            data.minimum_ha = status.get("minimum_ha");
            data.maximum_ha = status.get("maximum_ha");
            data.days_of_week_allowed = status.get("days_of_week_allowed");
            data.periods_allowed = status.get("periods_allowed");
            data.semester = purify(status.get("semester"), "semester");
            data.campus = purify(status.get("campus"), "campus");
            if (status.get("discipline")) {
                data.discipline = purify(status.get("discipline"), "discipline");
            }
            data.selectedDisciplines = [];
            data.teams = [];
            selectedDisciplines.each(function (discipline) {
                if (discipline.get("_custom")) {
                    data.selectedDisciplines.push(_.omit(discipline.toJSON(), "_color"));
                } else {
                    data.selectedDisciplines.push({
                        "id": purify(discipline.id, "discipline")
                    });
                }
                discipline.teams.each(function (team) {
                    var teamObj;
                    if (discipline.get("_custom")) {
                        teamObj = team.toJSON();
                        teamObj.schedules = team.schedules.toJSON();
                        teamObj.discipline = discipline.id;
                    } else {
                        teamObj = {
                            "id": purify(team.id, "team"),
                            "discipline": purify(discipline.id, "discipline"),
                            "_selected": team.get("_selected")
                        };
                    }
                    data.teams.push(teamObj);
                });
            });
            data.selectedCombination = selectedDisciplines.getSelectedCombination();
            this.set(data, {"silent": silent});
        }
    });
});