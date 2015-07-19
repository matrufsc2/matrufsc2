define("views/HomeView", [
    "templates",
    "underscore",
    "views/BaseView",
    "views/FiltersView",
    "views/SelectedDisciplinesView",
    "views/CalendarView",
    "views/PlansView",
    "views/SelectedTeamsView"
], function (templates, _, BaseView, FiltersView, SelectedDisciplinesView, CalendarView, PlansView, SelectedTeamsView) {
    "use strict";
    return BaseView.extend({
        "template": templates.home,
        "region": "main",
        "listen": {
            "render": "addSubViews"
        },
        "initialize": function (options) {
            _.extend(this, _.pick(options, [
                "campi",
                "selectedDisciplines",
                "semesters",
                "status",
                "history",
                "plan",
                "user",
                "possibilities"
            ]));
        },
        "addSubViews": function () {
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
                "status": this.status,
                "container": this.$("#calendar")
            }));
            this.subview("plans", new PlansView({
                "container": this.$("#plans-container"),
                "history": this.history,
                "status": this.status,
                "plan": this.plan,
                "possibilities": this.possibilities,
                "user": this.user,
                "selectedDisciplines": this.selectedDisciplines
            }));
            this.subview("selectedTeams", new SelectedTeamsView({
                "status": this.status,
                "selectedDisciplines": this.selectedDisciplines,
                "container": this.$("#teams-table-container")
            }));
        }
    });
});