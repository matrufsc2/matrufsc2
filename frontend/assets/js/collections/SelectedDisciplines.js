define("collections/SelectedDisciplines", [
    "collections/CachedCollection",
    "underscore",
    "please",
    "utils/combinator",
    "models/Discipline",
    "es6-promise"
], function (CachedCollection, _, Please, combinator, Discipline) {
    "use strict";
    return CachedCollection.extend({
        "model": Discipline,
        "conflicting": false,
        "combinationSelected": 0,
        "combinationsAvailable": [],
        "initialize": function (models, options) {
            _.extend(this, _.pick(options, ["status", "campi", "semesters"]));
            this.on("add remove", this.updateCombinations, this);
            this.listenTo(this.status, "change:campus", function () {
                this.reset();
                this.status.set({
                    "discipline": null
                });
            });
        },
        "updateCombinations": function (defaultCombination) {
            var collection = this;
            collection.teamsRequests = [];
            return Promise.all(this.map(function (discipline) {
                var color = discipline.get("_color");
                while (!color) {
                    color = Please.make_color({
                        "saturation": 0.5,
                        "value": (Math.floor(Math.random() * 25) + 75) / 100
                    })[0];
                    if (collection.findWhere({"_color": color}) !== undefined) {
                        color = null;
                        continue;
                    }
                    discipline.set({
                        "_color": color
                    });
                }
            }))
                .then(_.bind(this.detectCombinations, this))
                .then(function () {
                    collection.combinationSelected = _.isNumber(defaultCombination) ? defaultCombination : 0;
                })
                .then(_.bind(this.selectCombination, this));
        },
        "detectCombinations": function () {
            var onGetSchedule = function (schedule) {
                return schedule.get("hourStart") + ":" + schedule.get("minuteStart") + ":" + schedule.get("dayOfWeek") + ":" + schedule.get("classRepeat");
            };
            var onGetTeam = function (team) {
                return _.map(team.schedules.sortBy(onGetSchedule), onGetSchedule).join("|");
            };
            var teams = this.reduce(function (old, discipline) {
                if (this.status.get("editing") === true && this.status.get("discipline") === discipline.id) {
                    if (discipline.team) {
                        old.push([discipline.team]);
                    }
                    return old;
                }
                discipline.team = null;
                var modelTeams = discipline.teams.clone();
                var uniqueSchedules = [];
                modelTeams = modelTeams.filter(function (team) {
                    if (!team.get("_selected") || (team.discipline.get("_custom") !== true && team.getNumberOfLessons() === 0)) {
                        // Ignore teams which are not selected or teams that yet does not have lessons
                        return false;
                    }
                    var schedule = onGetTeam(team);
                    var result = uniqueSchedules.indexOf(schedule) === -1;
                    if (result) {
                        uniqueSchedules.push(schedule);
                    }
                    return result;
                });
                if (modelTeams.length > 0) {
                    old.push(modelTeams);
                }
                return old;
            }, [], this);
            this.map(function (discipline) {
                discipline.unset("_title");
            });
            var combinations = [];
            var maximumDisciplines = this.status.get("maximum_disciplines");
            if (!maximumDisciplines) {
                maximumDisciplines = teams.length;
            }
            var minimumDisciplines = this.status.get("minimum_disciplines");
            if (!minimumDisciplines) {
                minimumDisciplines = teams.length; // To maintain normal behavior
            }
            for(var c=maximumDisciplines; c>=minimumDisciplines; c--) {
                 combinations = combinations.concat(combinator(_.clone(teams), c));
            }
            if (maximumDisciplines !== null && minimumDisciplines !== null && combinations.length === 0) {
                this.map(function(discipline) {
                    discipline.set({
                        "_title": "Não há combinações disponíveis dado as configurações de combinação (número de disciplinas minimo/máximo) selecionadas"
                    });
                });
                this.combinationsAvailable = [];
                return;
            }
            var maximumHA = this.status.get("maximum_ha");
            var minimumHA = this.status.get("minimum_ha");
            var periods = this.status.get("periods_allowed");
            var daysOfWeeks = this.status.get("days_of_week_allowed") || [];
            combinations = _.filter(combinations, function (combination) {
                var disciplines = [];
                for (var c = combination.length; c--;) {
                    if (disciplines.indexOf(combination[c].discipline.id) !== -1) {
                        return false;
                    }
                    disciplines.push(combination[c].discipline.id);
                }
                var schedules = combination.reduce(function (old, team) {
                    return old.concat(team.schedules.map(function (schedule) {
                        schedule.team = team;
                        return schedule;
                    }));
                }, []);
                var totalHours = _.reduce(combination, function (total, team) {
                    return total + (team ? team.getNumberOfLessons() : 0);
                }, 0);
                if (minimumHA && minimumHA > totalHours) {
                    return false;
                }
                if (maximumHA && maximumHA < totalHours) {
                    return false;
                }
                for (c = schedules.length; c--;) {
                    var schedule = schedules[c];
                    if (!schedule.team.discipline.get("_custom")) {
                        var schedulePeriod = schedule.getPeriod();
                        for (var d=0; d<schedulePeriod.length; d++) {
                            if (periods.indexOf(schedulePeriod[d]) === -1) {
                                return false;
                            }
                        }
                        if (daysOfWeeks.indexOf(schedule.getDayOfWeek()) === -1) {
                            return false;
                        }
                    }
                }
                return true;
            });
            var disciplinesConflicted = {};
            var combinationsAvailable = _.filter(combinations, function(combination) {
                var schedules = combination.reduce(function (old, team) {
                    return old.concat(team.schedules.map(function (schedule) {
                        schedule.team = team;
                        return schedule;
                    }));
                }, []);
                for (c = schedules.length; c--;) {
                    var schedule = schedules[c];
                    var conflicts = _.filter(schedules, schedule.conflictsWith, schedule);
                    conflicts = _.reject(conflicts, _.matcher({
                        "id": schedule.id
                    }));
                    if (conflicts.length > 0) {
                        var disciplineId = schedule.team.discipline.id;
                        disciplinesConflicted[disciplineId] = disciplinesConflicted[disciplineId] || [];
                        disciplinesConflicted[disciplineId].push([schedule.team.id, conflicts]);
                        return false;
                    }
                }
                return true;
            });
            this.conflicting = false;
            if (combinationsAvailable.length === 0 && teams.length > 0) {
                this.conflicting = _.reduce(disciplinesConflicted, function (old, reg, discipline_id) {
                    var teamsDiscipline = _.pluck(reg, 0);
                    var teamsSelected = _.reduce(teams, function (old, disciplineTeams) {
                        if (old.length > 0) {
                            return old;
                        }
                        if (_.every(disciplineTeams, function (team) {
                                return team.discipline.id === discipline_id;
                            })) {
                            return disciplineTeams;
                        }
                        return old;
                    }, []);
                    var disciplineConflict = _.every(teamsSelected, function (team) {
                        var result = teamsDiscipline.indexOf(team.id) !== -1;
                        var schedules = team.schedules.map(function (schedule) {
                            schedule.team = team;
                            return schedule;
                        });
                        for (c = schedules.length; c--;) {
                            var schedule = schedules[c];
                            if (!team.discipline.get("_custom")) {
                                var schedulePeriod = schedule.getPeriod();
                                for (var d=0; d<schedulePeriod.length; d++) {
                                    if (periods.indexOf(schedulePeriod[d]) === -1) {
                                        result = false;
                                    }
                                }
                                if (daysOfWeeks.indexOf(schedule.getDayOfWeek()) === -1) {
                                    result = false;
                                }
                            }
                        }
                        return result;
                    });
                    if (disciplineConflict) {
                        var conflicts = _.pluck(
                            _.pluck(
                                _.pluck(
                                    _.flatten(
                                        _.pluck(reg, 1),
                                        true
                                    ),
                                    "team"
                                ),
                                "discipline"
                            ),
                            "id"
                        );
                        conflicts = conflicts.concat([discipline_id]);
                        conflicts = _.uniq(conflicts);
                        for(var c=0; c<conflicts.length; c++) {
                            var discipline = this.get(conflicts[c]);
                            discipline.set("_title", "Esta disciplina está impedindo a geração de uma combinação válida");
                        }

                    }
                    return disciplineConflict || old;
                }, this.conflicting, this);
                if (this.conflicting) {
                    combinationsAvailable = combinations;
                } else {
                    this.map(function(discipline) {
                        discipline.set({
                            "_title": "Não há combinações disponíveis dado as configurações de combinação selecionadas"
                        });
                    });
                }
            }
            this.combinationsAvailable = combinationsAvailable;
        },
        "combinationCount": function () {
            return this.combinationsAvailable.length;
        },
        "getSelectedCombination": function () {
            return this.combinationSelected;
        },
        "isConflicting": function () {
            return this.conflicting;
        },
        "setSelectedCombination": function (id) {
            var old = this.combinationSelected;
            this.combinationSelected = id;
            if (this.hasNextCombination() === false && this.hasPreviousCombination() === false) {
                this.combinationsAvailable = old;
                return false;
            }
            this.selectCombination();
            return true;
        },
        "selectCombination": function () {
            var combination = this.combinationsAvailable[this.combinationSelected];
            if (!combination) {
                this.trigger("change:combination");
                return;
            }
            this.map(function (discipline) {
                discipline.team = _.findWhere(combination, {
                    "discipline": discipline
                });
                discipline.semester = this.semesters.get(this.status.get("semester"));
                discipline.campus = this.campi.get(this.status.get("campus"));
            }, this);
            this.trigger("change:combination");
        },
        "nextCombination": function () {
            if (this.hasNextCombination()) {
                this.combinationSelected++;
            } else {
                this.combinationSelected = 0;
            }
            this.selectCombination();
        },
        "hasNextCombination": function () {
            return (this.combinationCount() - 1) > this.getSelectedCombination();
        },
        "previousCombination": function () {
            if (this.hasPreviousCombination()) {
                this.combinationSelected--;
            } else {
                this.combinationSelected = this.combinationCount() - 1;
            }
            this.selectCombination();
        },
        "hasPreviousCombination": function () {
            return 0 < this.getSelectedCombination();
        },
        "move": function (model, delta) {
            var index = this.indexOf(model);
            if ((delta < 0 && index > 0) || (delta > 0 && index < (this.length - 1))) {
                this.moveTo(model, index + delta);//Moves the actual model
            }
        },
        "moveTo": function (model, index) {
            if (!model) {
                return;
            }
            this.remove(model, {"silent": true});
            model.collection = this;
            this.add(model, {"at": index, "silent": true});
            this.trigger("sort");
        },
        "moveUp": function (model) {
            this.move(model, -1);
        },
        "moveDown": function (model) {
            this.move(model, 1);
        }
    });
});