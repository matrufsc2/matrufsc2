define("controllers/HomeController", [
	"underscore",
	"backbone",
	"chaplin",
	"bluebird",
	"collections/Campi",
	"collections/Disciplines",
	"collections/Semesters",
	"collections/SelectedDisciplines",
	"controllers/BaseController",
	"models/Status",
	"views/HomeView"
	], function(
		_,
		Backbone,
		Chaplin,
		Promise,
		Campi,
		Disciplines,
		Semesters,
		SelectedDisciplines,
		BaseController,
		Status,
		HomeView
	){
	"use strict";
	return BaseController.extend({
		"index": function(params, metadata, request){
			this.adjustTitle("");
			this.disciplines = new Disciplines();
			this.campi = new Campi();
			this.semesters = new Semesters();
			this.status = new Status(null, {
				"disciplines": this.disciplines,
				"campi": this.campi,
				"semesters": this.semesters
			});
			this.selectedDisciplines = new SelectedDisciplines([],{
				"parentCollection": this.disciplines,
				"status": this.status,
				"semesters": this.semesters,
				"campi": this.campi
			});
			this.view = new HomeView({
				"campi": this.campi,
				"disciplines": this.disciplines,
				"selectedDisciplines": this.selectedDisciplines,
				"semesters": this.semesters,
				"status" : this.status
			});
			var statusSessionKeys = ["semester","campus","discipline", "selectedDisciplines", "disabledTeams", "selectedCombination"];
			var statusSession = _.pick(request.query, statusSessionKeys);
			var updateStatusSession = _.bind(function() {
				this.status.on("change", function () {
					_.extend(statusSession, this.status.pick(["semester", "campus", "discipline"]));
					var url = Chaplin.utils.reverse("Home#index", statusSession, {"trigger": false});
					Backbone.history.navigate(url, {"trigger": false, "replace": false});
				}, this);
				this.selectedDisciplines.on("add change remove change:combination", function () {
					var selectedDisciplines = [];
					var allDisabledTeams = [];
					this.selectedDisciplines.each(function (discipline) {
						var disabledTeams = [];
						selectedDisciplines.push(discipline.id);
						discipline.teams.each(function (team) {
							if (team.get("_selected")) {
								return;
							}
							disabledTeams.push(team.id);
						});
						allDisabledTeams.push(disabledTeams.join(","));
					});
					statusSession.selectedDisciplines = selectedDisciplines;
					statusSession.disabledTeams = allDisabledTeams;
					statusSession.selectedCombination = this.selectedDisciplines.getSelectedCombination();
					var url = Chaplin.utils.reverse("Home#index", statusSession, {"trigger": false});
					Backbone.history.navigate(url, {"trigger": false, "replace": false});
				}, this);
			}, this);
			if(_.size(statusSession) === statusSessionKeys.length) {
				this.disciplines.once("sync", function(){
					var selectedDisciplinesIDs = statusSession.selectedDisciplines || [];
					Promise.all(_.filter(_.map(selectedDisciplinesIDs, function(selectedDisciplineID, key) {
						var discipline = this.disciplines.get(selectedDisciplineID);
						if(!discipline){
							return false;
						}
						var teams = statusSession.disabledTeams ? statusSession.disabledTeams[key]||"" : "";
						teams = teams.split(",");
						return discipline.select().then(function(){
							for(var c=0,l=teams.length,team;c<l; ++c){
								team = teams[c];
								team = this.teams.findWhere({
									"id": parseInt(team)
								});
								if(!!team) {
									team.set({
										"_selected": false
									});
								}
							}
						});
					}, this), function(discipline) {
						return !!discipline;
					})).bind(this).then(function(){
						this.selectedDisciplines.updateCombinations(parseInt(statusSession.selectedCombination)).then(function(){
							this.status.set({
								"discipline": statusSession.discipline
							});
							updateStatusSession();
						});
					});
				}, this);
				this.campi.once('sync', function(){
					this.status.set(_.pick(statusSession, "campus"));
					this.disciplines.trigger("sync");
				}, this);
				this.status.set(_.pick(statusSession, "semester"));
				this.campi.trigger("sync");
			} else {
				updateStatusSession();
			}
			window.h = this;
			this.semesters.fetch();
			this.status.listenEvents();
		}
	});
});
