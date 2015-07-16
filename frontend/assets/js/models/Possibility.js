define("models/Possibility", [
    "models/BaseModel",
    "models/Discipline",
    "models/Team",
    "underscore",
    "es6-promise"
], function(BaseModel, Discipline, Team, _) {
    "use strict";
    function purify(id, type) {
        return (id || "").replace("matrufsc2-"+type+"-", "");
    }
    function unpurify(id, type) {
        return "matrufsc2-"+type+"-"+purify(id, type);
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
        "loadPossibility": function(status, selectedDisciplines) {
            var statusSession = this.toJSON();
            selectedDisciplines.reset();
            return new Promise(function(resolve, reject) {
                if (status.get("editing")) {
                    return reject("Saia do modo de edição antes de carregar outro plano");
                }
                status.set({
                    "discipline": null
                });
                status.once("change:campus", function () {
                    Promise.all(_.map(statusSession.selectedDisciplines, function (selectedDiscipline) {
                        var discipline;
                        var promiseList;
                        if (selectedDiscipline._custom) {
                            discipline = new Discipline(selectedDiscipline);
                            discipline.campus = status.get("campus");
                            promiseList = [discipline.select()];
                        } else {
                            discipline = new Discipline({
                                "id": unpurify(selectedDiscipline.id, "discipline")
                            });
                            discipline.campus = status.get("campus");
                            promiseList = [discipline.fetch(), discipline.select()];
                        }

                        return Promise.all(promiseList).then(_.bind(function () {
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
                                        return Promise.reject("Foram encontradas turmas que nao existem mais na disciplina "+discipline.get("name"));
                                    }
                                }, this)
                            ).then(function(){
                                selectedDisciplines.add(discipline);
                            });
                        }, this));
                    }, this)).then(function(){
                        return selectedDisciplines.updateCombinations(
                            statusSession.selectedCombination
                        );
                    }).then(function() {
                        if (statusSession.discipline) {
                            status.set({
                                "discipline": unpurify(statusSession.discipline, "discipline")
                            });
                        }
                        resolve();
                    }, reject);
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
                } else {
                    status.trigger("change:campus");
                }
            });
        },
        "savePossibility": function(status, selectedDisciplines, silent) {
            if (this.disposed || !status || !selectedDisciplines) {
                return;
            }
            var data = {};
            data.semester = purify(status.get("semester"), "semester");
            data.campus = purify(status.get("campus"), "campus");
            if(status.get("discipline")) {
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