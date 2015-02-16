define("models/Plan", [
    "models/BaseModel",
    "models/Discipline",
    "models/Team",
    "bluebird",
    "underscore",
    "jquery",
    "moment"
], function(BaseModel, Discipline, Team, Promise, _, $, moment) {
    "use strict";
    function purify(id, type) {
        return (id || "").replace("matrufsc2-"+type+"-", "");
    }
    function unpurify(id, type) {
        return "matrufsc2-"+type+"-"+purify(id, type);
    }
    return BaseModel.extend({
        "urlRoot": "/api/plans/",
        "defaults": {
            "id": null,
            "history": [],
            "data": {
                "selectedDisciplines": [],
                "semester": null,
                "campus": null,
                "teams": [],
                "discipline": null,
                "selectedCombination": 0
            }
        },
        "loadPlan": function(status, selectedDisciplines, history, version) {
            var statusSession;
            if (!version) {
                statusSession = this.get("data");
            } else {
                if (_.isNaN(parseInt(version))) {
                    return alert("Versao invalida: "+version);
                }
                statusSession = _.findWhere(this.get("history"), {
                    "id": parseInt(version)
                });
                if (statusSession) {
                    statusSession = statusSession.data;
                } else {
                    alert("Versao '"+version+"' nao encontrada");
                }
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
                        promiseList = [discipline.select()];
                    } else {
                        discipline = new Discipline({
                            "id": unpurify(selectedDiscipline.id, "discipline")
                        });
                        promiseList = [discipline.fetch(), discipline.select()];
                    }

                    return Promise.all(promiseList).bind(this).then(function () {
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
                    });
                }, this)).bind(this).then(function(){
                    return selectedDisciplines.updateCombinations(
                        statusSession.selectedCombination
                    );
                }).then(function() {
                    if (_.has(statusSession, "discipline")) {
                        status.set({
                            "discipline": unpurify(statusSession.discipline, "discipline")
                        });
                    }
                    this.trigger("loaded");
                }, function(err){
                        if (_.isString(err)) {
                            var error_container = $("#error-discipline");
                            error_container.find("p").html(err);
                            error_container.foundation("reveal", "open");
                        }
                    }
                );
                var campus = unpurify(statusSession.campus, "campus");
                if (status.get("campus") !== campus) {
                    status.set({
                        "campus": campus
                    });
                } else {
                    status.trigger("change:campus");
                }

            }, this);
            var semester = unpurify(statusSession.semester, "semester");
            if (semester !== status.get("semester")) {
                status.set({
                    "semester": semester
                });
            } else {
                status.trigger("change:campus");
            }
            history.set(this.get("history"), {"sort": true});
        },
        "savePlan": function(status, selectedDisciplines, history, silent) {
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
            this.set({
                "data": data,
                "history": this.get("history").concat([{
                    "id": moment.utc().unix(),
                    "data": data
                }])
            }, {"silent": silent});
            history.set(this.get("history"), {"sort": true});
        }
    });
});