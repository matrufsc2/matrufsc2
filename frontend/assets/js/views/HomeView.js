define("views/HomeView", [
	"templates",
	"underscore",
	"views/BaseView",
	"views/FiltersView",
	"views/SelectedDisciplinesView",
	"views/CalendarView",
	"views/SelectedTeamsView"
], function(templates, _, BaseView, FiltersView, SelectedDisciplinesView, CalendarView, SelectedTeamsView){
	"use strict";
	return BaseView.extend({
		"template" : templates.home,
		"region"   : "main",
		"listen"    : {
			"render": "addSubViews"
		},
		"initialize": function(options) {
			_.extend(this, _.pick(options, [
				"campi",
				"selectedDisciplines",
				"semesters",
				"status"
			]));
		},
		"addSubViews": function(){
			this.subview("filters", new FiltersView({
				"semesters": this.semesters,
				"campi": this.campi,
				"status": this.status,
				"selectedDisciplines": this.selectedDisciplines,
				"container": this.$("#filters")
			}));
			this.subview("selectedDisciplines", new SelectedDisciplinesView({
				"collection": this.selectedDisciplines,
				"status": this.status,
				"container": this.$("#disciplines-resume")
			}));
			this.subview("calendar", new CalendarView({
				"collection": this.selectedDisciplines,
				"container": this.$("#calendar")
			}));
			this.subview("selectedTeams", new SelectedTeamsView({
				"status": this.status,
				"selectedDisciplines": this.selectedDisciplines,
				"container": this.$("#teams-table-container")
			}));
		}
	});
});