define("views/SelectedTeamsView", [
		"templates",
		"views/BaseView",
		"chaplin",
		"underscore",
		"views/SelectedTeamView",
		"collections/Teams"
], function(templates, BaseView, Chaplin, _, selectedTeamView, Teams){
	"use strict";
	var SelectedTeamsView = BaseView.extend({
		"template" : templates.selectedTeams,
		"itemView": selectedTeamView,
		"listSelector": "tbody",
		"tagName": "table",
        "useCssAnimation": true,
        "animationStartClass": "animation-fade-in",
        "animationEndClass": "animation-fade-in-end",
        "animationDuration": 1500,
		"listen": {
			"addedToDOM": "applyFoundation"
		},
		"events": {
			"click #groupTeams": "groupTeams"
		},
		"initialize": function(options){
			this.collection = null;
			_.extend(this, _.pick(options, ["selectedDisciplines", "status"]));
			this.collection = new Teams();
            this.disciplineCollection = null;
			this.updateCollection();
			BaseView.prototype.initialize.apply(this, []);
			Chaplin.CollectionView.prototype.initialize.apply(this, []);
			this.listenTo(this.status, "change:discipline", this.selectDiscipline);
			this.groupEnabled = this.checkGroupTeamsEnabled();
		},
		"checkGroupTeamsEnabled": function(){
			return this.$("#groupTeams").is(":checked");
		},
		"groupTeams": function(){
			this.groupEnabled = this.checkGroupTeamsEnabled();
			this.group();
			_.each(this.getItemViews(), function(view) {
				view.render();
			}, this);
		},
		"group": function(){
            if (!this.disciplineCollection) {
                return;
            }
            if(!this.groupEnabled) {
                this.disciplineCollection.each(function(team){
                    team.startGrouping = false;
                    team.endGrouping = false;
                    this.collection.add(team);
                }, this);
				return;
			}
			var onGetSchedule = function(schedule) {
				return schedule.get("hourStart")+""+schedule.get("minuteStart")+":"+schedule.get("dayOfWeek")+":"+schedule.get("classRepeat");
			};
			var onGetTeam = function(team) {
				return _.map(team.schedules.sortBy(onGetSchedule), onGetSchedule).join("|");
			};
            var teams_schedules = {};
			this.disciplineCollection.each(function(team) {
                var key = onGetTeam(team);
                if (!teams_schedules[key]) {
                    teams_schedules[key] = [];
                }
                teams_schedules[key].push(team);
            });
            _.each(teams_schedules, function(teams) {
                var teamsLastIndex = teams.length - 1;
                _.each(teams, function(team, index){
                    team.startGrouping = index === 0;
                    team.endGrouping = index === teamsLastIndex;
                    this.collection.add(team);
                }, this);
            }, this);
		},
		"updateCollection": function(){
			if(!!this.collection) {
				this.stopListening(this.collection);
			}
			var selectedDiscipline = this.status.get("discipline");
			var discipline = this.selectedDisciplines.get(selectedDiscipline);
            this.collection.reset();
			if(!selectedDiscipline || !discipline) {
				return;
			}
			this.disciplineCollection = discipline.teams;
			this.groupTeams();
		},
		"selectDiscipline": function(){
			this.updateCollection();
			this.renderAllItems();
		},
		"initItemView": function(model) {
			if (this.itemView) {
				return new this.itemView({
					autoRender: false,
					model: model,
					selectedDisciplines: this.selectedDisciplines
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
		"getTemplateData": function(){
			return {
				"view": this
			};
		},
		"render": function(){
			this.group();
			BaseView.prototype.render.apply(this, []);
			Chaplin.CollectionView.prototype.render.apply(this, []);
		}
	});
	_.extend(SelectedTeamsView.prototype,
		_.omit(
			Chaplin.CollectionView.prototype,
			_.keys(SelectedTeamsView.prototype),
			_.keys(BaseView.prototype)
		)
	);
	return SelectedTeamsView;
});