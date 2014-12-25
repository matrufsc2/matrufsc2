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
			function purify(id, type) {
				return (id || "").replace("matrufsc2-"+type+"-", "");
			}
			function unpurify(id, type) {
				return "matrufsc2-"+type+"-"+purify(id, type);
			}
			var updateURL = _.bind(function() {
				if (this.disposed || !this.status || !this.selectedDisciplines) {
					return;
				}
				var urlQuery = {};
				urlQuery.semester = purify(this.status.get("semester"), "semester");
				urlQuery.campus = purify(this.status.get("campus"), "campus");
				var title = "";
				var semester, campus;
				if ((semester = this.semesters.get(this.status.get("semester")))) {
					title += "Semestre " + semester.get("name");
					if ((campus = this.campi.get(this.status.get("campus")))) {
						title += " - Campus "+campus.get("name");
					}
				}
				this.adjustTitle(title);
				if(this.status.get("discipline")) {
					urlQuery.discipline = purify(this.status.get("discipline"), "discipline");
				}
				var selectedDisciplines = [];
				var disabledTeams = [];
				this.selectedDisciplines.each(function (discipline) {
					selectedDisciplines.push(purify(discipline.id, "discipline"));
					discipline.teams.each(function (team) {
						if (team.get("_selected")) {
							return;
						}
						disabledTeams.push(purify(team.id, "team"));
					});
				});
				urlQuery.selectedDisciplines = selectedDisciplines.join(",");
				urlQuery.disabledTeams = disabledTeams.join(",");
				urlQuery.selectedCombination = this.selectedDisciplines.getSelectedCombination();
				if(!urlQuery.semester || !urlQuery.campus) {
					return;
				}
				var url = Chaplin.utils.reverse("Home#index", urlQuery);
				Backbone.history.navigate(url, {"trigger": false, "replace": false});
				var urlClean = Chaplin.utils.reverse(
					"Home#index",
					_.omit(
						urlQuery,
						"discipline",
						"selectedCombination"
					)
				);
				var history = this.getHistory();
				var model = history.findWhere({
					"url": urlClean
				});
				if (!model) {
					model = history.create({
						"url": urlClean
					});
				}
				model.save();
				history.sort();
				while (history.length > 10) {
					model = history.pop();
					model.collection = history;
					model.destroy();
				}
				this.getHeader().render();
			}, this);
			var listen = _.bind(function(){
				this.status.off("change", updateURL);
				this.selectedDisciplines.off("change change:combination", updateURL);
				this.status.on("change", updateURL);
				this.selectedDisciplines.on("change change:combination", updateURL);
			}, this);
			if (_.size(statusSession) >= 2) {
				// Well, Here we can load based on data in the querystring :D
				if (statusSession.selectedDisciplines && !_.isArray(statusSession.selectedDisciplines)) {
					statusSession.selectedDisciplines = statusSession.selectedDisciplines.split(",");
				}
				if (statusSession.disabledTeams && !_.isArray(statusSession.disabledTeams)) {
					statusSession.disabledTeams = statusSession.disabledTeams.split(",");
				}
				statusSession.selectedCombination = parseInt(statusSession.selectedCombination) || 0;
				statusSession.disabledTeams = statusSession.disabledTeams || [];
				statusSession.selectedDisciplines = statusSession.selectedDisciplines || [];
				this.semesters.once("sync", function () {
					this.status.once("change:campus", function () {
						this.disciplines.on("sync", function disciplinesLoaded() {
							Promise.all(_.map(statusSession.selectedDisciplines, function (selectedDiscipline) {
								var discipline = this.disciplines.get(unpurify(selectedDiscipline, "discipline"));
								if (!discipline) {
									return Promise.reject();
								}
								this.disciplines.off("sync", disciplinesLoaded, this);
								return discipline.select().bind(this).then(function () {
									return Promise.all(
										_.map(statusSession.disabledTeams, function (disabledTeam) {
											var team = discipline.teams.get(unpurify(disabledTeam, "team"));
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
											statusSession.selectedCombination
										)
									)
									.bind(this).then(function () {
										this.selectedDisciplines.trigger("change:combination");
										if (_.has(statusSession, "discipline")) {
											this.status.set({
												"discipline": unpurify(statusSession.discipline, "discipline")
											});
										}
									});
								});
							}, this)).then(listen, function(){});
						}, this);
						this.status.set({
							"campus": unpurify(statusSession.campus, "campus")
						});
					}, this);
					this.status.set({
						"semester": unpurify(statusSession.semester, "semester")
					});
				}, this);
			} else {
				listen();
			}
			this.status.listenEvents();
		}
	});
});
