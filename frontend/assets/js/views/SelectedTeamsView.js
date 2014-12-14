define("views/SelectedTeamsView", [
		"templates",
		"views/BaseView",
		"chaplin",
		"underscore",
		"fastdom",
		"views/SelectedTeamView",
		"collections/Teams"
], function(templates, BaseView, Chaplin, _, fastdom, selectedTeamView, Teams){
	"use strict";
	var SelectedTeamsView = BaseView.extend({
		"template" : templates.selectedTeams,
		"itemView": selectedTeamView,
		"listSelector": "tbody",
		"tagName": "table",
		"listen": {
			"addedToDOM": "applyFoundation"
		},
		"events": {
			"click #groupTeams": "groupTeams"
		},
		"initialize": function(options){
			this.collection = null;
			_.extend(this, _.pick(options, ["selectedDisciplines", "status"]));
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
			if(!this.groupEnabled || !this.collection) {
				if(this.collection) {
					this.collection.comparator = null;
					this.collection.each(function(team) {
						team.startGrouping = false;
					});
				}
				return;
			}
			var onGetSchedule = function(schedule) {
				return schedule.get("hourStart")+""+schedule.get("minuteStart")+":"+schedule.get("dayOfWeek")+":"+schedule.get("classRepeat");
			};
			var onGetTeam = function(team) {
				var schedules = _.map(team.schedules.sortBy(onGetSchedule), onGetSchedule).join("|");
				return schedules;
			};
			this.collection.comparator = onGetTeam;
			this.collection.sort({
				"silent": true
			});
			var oldTeam = null;
			this.collection.map(function(team){
				if(oldTeam === null) {
					oldTeam = team;
					oldTeam.startGrouping = false;
					return;
				}
				if(onGetTeam(team) === onGetTeam(oldTeam)) {
					team.startGrouping = false;
					oldTeam = team;
				} else {
					team.startGrouping = true;
					oldTeam = team;
				}
				return team;
			});
		},
		"updateCollection": function(){
			if(!!this.collection) {
				this.stopListening(this.collection);
			}
			var selectedDiscipline = this.status.get("discipline");
			var discipline = this.selectedDisciplines.get(selectedDiscipline);
			if(!selectedDiscipline || !discipline) {
				this.collection = new Teams();
				return;
			}
			this.collection = discipline.teams;
			this.addCollectionListeners();
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
					discipline: this.selectedDisciplines.get(this.status.get("discipline")) || null,
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
			fastdom.write(function() {
				Chaplin.CollectionView.prototype.render.apply(this, []);
			}, this);
		},
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