define("collections/SelectedDisciplines", [
	"collections/CachedCollection",
	"underscore",
	"moment",
	"please",
	"utils/combinator",
	"models/Discipline",
	"bluebird"
], function(CachedCollection, _, moment, Please, combinator, Discipline, Promise){
	"use strict";
	return CachedCollection.extend({
		"model": Discipline,
        "conflicting": false,
		"combinationSelected": 0,
		"combinationsAvailable": [],
		"initialize" : function(models, options){
			_.extend(this, _.pick(options, ["status", "campi", "semesters"]));
			this.on("add remove", this.updateCombinations, this);
            this.status = options.status;
			this.listenTo(this.status, "change:campus", function(){
				this.each(function(discipline) {
					discipline.unselect();
				});
                this.status.set({
                    "discipline": null
                });
			});
		},
		"updateCombinations": function(defaultCombination){
			var collection = this;
			collection.teamsRequests = [];
			return Promise.all(this.map(function(discipline) {
				var color = discipline.get("_color");
				while(!color) {
					color = Please.make_color({
						"saturation": 0.5,
						"value": (Math.floor(Math.random()*25)+75)/100
					});
					if(collection.findWhere({"_color": color}) !== undefined) {
						color = null;
						continue;
					}
					discipline.set({
						"_color": color
					});
				}
			}))
			.bind(this)
			.then(function(){
				this.combinationSelected = _.isNumber(defaultCombination)?defaultCombination:0;
			})
			.then(this.detectCombinations)
			.then(this.selectCombination);
		},
		"detectCombinations": function(){
			var onGetSchedule = function(schedule) {
				return schedule.get("hourStart")+":"+schedule.get("minuteStart")+":"+schedule.get("dayOfWeek")+":"+schedule.get("classRepeat");
			};
			var onGetTeam = function(team) {
				return _.map(team.schedules.sortBy(onGetSchedule), onGetSchedule).join("|");
			};
			var teams = this.reduce(function(old, discipline){
                if (this.status.get("editing") === true && this.status.get("discipline") === discipline.id) {
                    if (discipline.team) {
                        old.push([discipline.team]);
                    }
                    return old;
                }
				discipline.team = null;
				var modelTeams = discipline.teams.clone();
				var uniqueSchedules = [];
				modelTeams = modelTeams.filter(function(team) {
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
			var combinations = combinator(_.clone(teams), teams.length);
			this.map(function(discipline) {
				discipline.unset("_title");
			});
			var disciplinesConflicted = {};
			var combinationsAvailable = _.filter(combinations, function(combination){
				var disciplines = [];
				for(var c=combination.length; c--;) {
					if(disciplines.indexOf(combination[c].discipline.id) !== -1) {
						return false;
					}
					disciplines.push(combination[c].discipline.id);
				}
				var schedules = combination.reduce(function(old, team) {
					return old.concat(team.schedules.map(function(schedule) {
						schedule.team = team;
						return schedule;
					}));
				}, []);
				for(var verifySchedule = schedules.length; verifySchedule--;) {
					var schedule = schedules[verifySchedule];
					if (_.filter(schedules, schedule.conflictsWith, schedule).length > 1) {
                        var disciplineId = schedule.team.discipline.id;
                        disciplinesConflicted[disciplineId] = disciplinesConflicted[disciplineId] || [];
                        disciplinesConflicted[disciplineId].push(schedule.team.id);
                        return false;
					}
				}
				return true;
			});
			this.conflicting = false;
			if (combinationsAvailable.length === 0 && teams.length > 0) {
				this.conflicting =_.reduce(disciplinesConflicted, function(old, teamsDiscipline, discipline_id) {
					var teamsSelected = _.reduce(teams, function(old, disciplineTeams){
						if(old.length > 0) {
							return old;
						}
						if(_.every(disciplineTeams, function(team) {
							return team.discipline.id === discipline_id;
						})) {
							return disciplineTeams;
						}
						return old;
					}, []);
					var disciplineConflict = _.every(teamsSelected, function(team) {
						return teamsDiscipline.indexOf(team.id) > -1;
					});
					if (disciplineConflict) {
						var discipline = this.get(discipline_id);
						discipline.set("_title", "Esta disciplina esta impedindo a geracao de uma combinacao valida");
					}
					return disciplineConflict || old;
				}, this.conflicting, this);
                combinationsAvailable = _.filter(combinations, function(combination){
                    var disciplines = [];
                    for(var c=combination.length; c--;) {
                        if(disciplines.indexOf(combination[c].discipline.id) !== -1) {
                            return false;
                        }
                        disciplines.push(combination[c].discipline.id);
                    }
                    return true;
                });
			}
			this.combinationsAvailable = combinationsAvailable;
		},
		"combinationCount": function(){
			return this.combinationsAvailable.length;
		},
		"getSelectedCombination": function(){
			return this.combinationSelected;
		},
        "isConflicting": function() {
            return this.conflicting;
        },
		"setSelectedCombination": function(id){
			var old = this.combinationSelected;
			this.combinationSelected = id;
			if(this.hasNextCombination() === false && this.hasPreviousCombination() === false){
				this.combinationsAvailable = old;
				return false;
			}
			this.selectCombination();
			return true;
		},
		"selectCombination": function(){
			var combination = this.combinationsAvailable[this.combinationSelected];
			if(!combination) {
				this.trigger("change:combination");
				return;
			}
			this.map(function(discipline){
				discipline.team = _.findWhere(combination, {
					"discipline": discipline
				});
				discipline.semester = this.semesters.get(this.status.get("semester"));
				discipline.campus = this.campi.get(this.status.get("campus"));
			}, this);
			this.trigger("change:combination");
		},
		"nextCombination": function(){
			if(this.hasNextCombination()) {
				this.combinationSelected++;
			} else {
				this.combinationSelected = 0;
			}
			this.selectCombination();
		},
		"hasNextCombination": function(){
			return (this.combinationCount()-1) > this.getSelectedCombination();
		},
		"previousCombination": function(){
			if(this.hasPreviousCombination()) {
				this.combinationSelected--;
			} else {
				this.combinationSelected = this.combinationCount()-1;
			}
			this.selectCombination();
		},
		"hasPreviousCombination": function(){
			return 0 < this.getSelectedCombination();
		},
		"move": function(model, delta) {
			var index = this.indexOf(model);
			if ((delta < 0 && index > 0) || (delta > 0 && index < (this.length-1))) {
				this.moveTo(model, index+delta);//Moves the actual model
			}
		},
		"moveTo": function(model, index) {
			if(!model) {
				return;
			}
			this.remove(model, {"silent": true});
			model.collection = this;
			this.add(model, {"at": index, "silent": true});
			this.trigger("sort");
		},
		"moveUp": function(model) {
			this.move(model, -1);
		},
		"moveDown": function(model) {
			this.move(model, 1);
		}
	});
});