define("collections/SelectedDisciplines", ["query-engine", "underscore", "moment", "please", "utils/combinator", "models/Discipline", "bluebird"], function(QueryEngine, _, moment, Please, combinator, Discipline, Promise){
	"use strict";
	return QueryEngine.QueryCollection.extend({
		"model": Discipline,
		"combinationSelected": 0,
		"combinationsAvailable": [],
		"initialize" : function(models, options){
			options = _.defaults(options || {}, {
				"live": true,
				"updateAtInitialization": true
			});
			if(!!options.parentCollection){
				// QueryEngine for some reason needs a "hasModel" method to work
				// Here, i will overwrite this method on a parent collection, if one exists
				// In the future I will fix this bug on QueryEngine with a fork. 
				options.parentCollection.hasModel = _.bind(QueryEngine.QueryCollection.prototype.hasModel, options.parentCollection);
			}
			QueryEngine.QueryCollection.prototype.initialize.call(this, models, options);
			if(options.parentCollection && options.parentCollection.model !== this.model) {
				throw "Invalid parent collection";
			}
			_.extend(this, _.pick(options, ["status", "campi", "semesters"]));
			this.setQuery("onlySelected", {
				"_selected": true
			});
			if(options.live) {
				this.on("add remove", this.updateCombinations, this);
			} 
			if(options.updateAtInitialization) {
				this.query();
				this.updateCombinations();
			}
		},
		"updateCombinations": function(defaultCombination){
			var collection = this;
			return Promise.all(this.map(function(discipline) {
				discipline.collection = collection;
				var color = discipline.get("_color");
				while(!color) {
					color = Please.make_color({
						"saturation": 0.5,
						"value": 0.8
					})
					if(collection.findWhere({"_color": color}) !== undefined) {
						color = null;
						continue;
					}
					discipline.set({
						"_color": color
					});
				}
				return discipline.teams.fetch();
			}))
			.bind(this)
			.then(function(){
				this.combinationSelected = _.isNumber(defaultCombination)?defaultCombination:0;
			})
			.then(this.detectCombinations)
			.then(this.selectCombination);
		},
		"detectCombinations": function(){
			var teams = this.reduce(function(old, discipline){
				discipline.team = null;
				var modelTeams = discipline.teams.clone();
				return old.concat(modelTeams.map(function(team){
					team.discipline = discipline;
					return team;
				}));
			}, []);
			teams = _.filter(teams, function(team){
				return team.get("_selected");
			});
			var combinations = combinator(_.map(teams, function(team){
				return [team];
			}), _.reduce(teams, function(old, team) {
				if(old.indexOf(team.discipline.get("code")) === -1){
					old.push(team.discipline.get("code"));
				}
				return old;
			}, []).length);
			this.combinationsAvailable = _.filter(combinations, function(combination){
				var disciplines = [];
				for(var c=combination.length; c--;) {
					if(disciplines.indexOf(combination[c].discipline.id) !== -1) {
						return false;
					}
					disciplines.push(combination[c].discipline.id);
				}
				var schedules = combination.reduce(function(old, team) {
					return old.concat(team.schedules.clone().models);
				}, []);
				for(var verifySchedule = schedules.length; verifySchedule--;) {
					var schedule = schedules[verifySchedule];
					for(var count = schedules.length; count--;) {
						if(verifySchedule === count) {
							continue;
						}
						if (schedule.conflictsWith(schedules[count])){
							return false;
						}
					}
				}
				return true;
			});
		},
		"combinationCount": function(){
			return this.combinationsAvailable.length;
		},
		"getSelectedCombination": function(){
			return this.combinationSelected;
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
				var team = _.findWhere(combination, {
					"discipline": discipline
				});
				discipline.team = team;
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
			return this.combinationCount() > this.getSelectedCombination();
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
			if ((delta < 0 && index+delta >= 0) || (delta > 0 && index+delta < this.length)) {
				this.moveTo(this.at(index+delta), index-delta);// Moves the old model
				this.moveTo(model, index+delta);//Moves the actual model
			}
		},
		"moveTo": function(model, index) {
			if(!model) {
				return;
			}
			this.remove(model, {"silent": true});
			this.add(model, {"at": index});
		},
		"moveUp": function(model) {
			this.move(model, -1);
		},
		"moveDown": function(model) {
			this.move(model, 1);
		}
	});
});