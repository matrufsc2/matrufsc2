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
			var statusSessionKeys = [
				"semester",
				"campus",
				"discipline",
				"selectedDisciplines",
				"disabledTeams",
				"selectedCombination"
			];
			var statusSession = _.pick(request.query, statusSessionKeys) || {};
			var updateURL = _.bind(function() {
				if (this.disposed || !this.status || !this.selectedDisciplines) {
					return;
				}
				var urlQuery = {};
				urlQuery.semester = this.status.get("semester");
				urlQuery.campus = this.status.get("campus");
				urlQuery.discipline = this.status.get("discipline");
				var selectedDisciplines = [];
				var disabledTeams = [];
				this.selectedDisciplines.each(function (discipline) {
					selectedDisciplines.push(discipline.id);
					discipline.teams.each(function (team) {
						if (team.get("_selected")) {
							return;
						}
						disabledTeams.push(team.id);
					});
				});
				urlQuery.selectedDisciplines = selectedDisciplines;
				urlQuery.disabledTeams = disabledTeams;
				urlQuery.selectedCombination = this.selectedDisciplines.getSelectedCombination();
				var url = Chaplin.utils.reverse("Home#index", urlQuery);
				Backbone.history.navigate(url, {"trigger": false, "replace": false});
			}, this);
			if (_.size(statusSession) >= 2) {
				// Well, Here we can load based on data in the querystring :D
				if (statusSession.selectedDisciplines && !_.isArray(statusSession.selectedDisciplines)) {
					statusSession.selectedDisciplines = [statusSession.selectedDisciplines];
				}
				if (statusSession.disabledTeams && !_.isArray(statusSession.disabledTeams)) {
					statusSession.disabledTeams = [statusSession.disabledTeams];
				}
				this.semesters.once("sync", function(){
					this.status.once("change:campus", function() {
						this.disciplines.on("sync", function disciplinesLoaded(){
							if (!_.has(statusSession, "selectedDisciplines")) {
								this.status.on("change", updateURL);
								this.selectedDisciplines.on("change change:combination", updateURL);
								return;
							}
							_.each(statusSession.selectedDisciplines || [], function(selectedDiscipline){
								var discipline = this.disciplines.get(selectedDiscipline);
								if (!discipline) {
									return;
								}
								this.disciplines.off("sync", disciplinesLoaded, this);
								discipline.select().bind(this).then(function(){
									Promise.all(
										_.map(statusSession.disabledTeams || [], function(disabledTeam) {
											var team = discipline.teams.get(disabledTeam);
											if (team) {
												team.set({"_selected": false});
												return this.selectedDisciplines.updateCombinations();
											} else {
												return Promise.resolve();
											}
										}, this)
										)
										.then(
											this.selectedDisciplines.updateCombinations(
												parseInt(statusSession.selectedCombination) || 0
											)
										)
										.bind(this).then(function(){
											this.selectedDisciplines.trigger("change:combination");
											if (_.has(statusSession, "discipline")) {
												this.status.set({
													"discipline": statusSession.discipline
												});
											}
										});
								});
							}, this);
						}, this);
						this.status.set({
							"campus": statusSession.campus
						});
					}, this);
					this.status.set({
						"semester": statusSession.semester
					});
				}, this);
			} else {
				this.status.on("change", updateURL);
				this.selectedDisciplines.on("change change:combination", updateURL);
			}
			this.status.listenEvents();
		}
	});
});
