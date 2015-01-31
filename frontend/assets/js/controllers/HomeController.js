define("controllers/HomeController", [
    "underscore",
    "backbone",
    "chaplin",
    "bluebird",
    "collections/Campi",
    "collections/Semesters",
    "collections/SelectedDisciplines",
    "collections/HistoryCollection",
    "controllers/BaseController",
    "models/Status",
    "models/Discipline",
    "models/Plan",
    "views/HeaderView",
    "views/HomeView"
], function (_,
             Backbone,
             Chaplin,
             Promise,
             Campi,
             Semesters,
             SelectedDisciplines,
             HistoryCollection,
             BaseController,
             Status,
             Discipline,
             Plan,
             HeaderView,
             HomeView) {
    "use strict";
    return BaseController.extend({
        "initialize": function () {
            BaseController.prototype.initialize.call(this);
            this.historyCollection = null;
            this.plan = new Plan();
            this.campi = new Campi();
            this.semesters = new Semesters();
        },
        "getHistory": function () {
            if (!this.historyCollection || this.historyCollection.disposed) {
                this.historyCollection = new HistoryCollection();
            }
            this.historyCollection.sort();
            return this.historyCollection;
        },
        "getHeader": function () {
            if (!this.header || this.header.disposed) {
                this.header = new HeaderView({
                    "historyCollectionGetter": _.bind(this.getHistory, this),
                    "plan": this.plan,
                    "route": this.route,
                    "user": this.user
                });
            }
            return this.header;
        },
        "index": function (params, metadata, request) {
            this.adjustTitle("");
            this.status = new Status(null, {
                "campi": this.campi,
                "semesters": this.semesters
            });
            this.selectedDisciplines = new SelectedDisciplines([], {
                "status": this.status,
                "semesters": this.semesters,
                "campi": this.campi
            });
            this.view = new HomeView({
                "campi": this.campi,
                "selectedDisciplines": this.selectedDisciplines,
                "semesters": this.semesters,
                "status": this.status,
                "history": this.getHistory(),
                "plan": this.plan,
                "user": this.user
            });
            var statusSessionKeys = [
                "plan",
                "version"
            ];
            var statusSession = _.pick(request.query, statusSessionKeys) || {};
            var listen = _.bind(function () {
                this.plan.on("change:_version", function(){
                    this.plan.loadPlan(
                        this.status,
                        this.selectedDisciplines,
                        this.getHistory(),
                        this.plan.get("_version")
                    );
                }, this);
                this.plan.on("change", function(){
                    var url = Chaplin.utils.reverse("Home#index", {
                        "plan": this.plan.id,
                        "version": this.plan.get("_version")
                    });
                    Backbone.history.navigate(url, {"trigger": false, "replace": false});
                }, this);
            }, this);
            var updateTitle = _.bind(function () {
                var title = "";
                var semester, campus;
                if ((semester = this.semesters.get(this.status.get("semester")))) {
                    title += "Semestre " + semester.get("name");
                    if ((campus = this.campi.get(this.status.get("campus")))) {
                        title += " - Campus " + campus.get("name");
                    }
                }
                this.adjustTitle(title);
            }, this);
            this.status.on("change", updateTitle);
            this.selectedDisciplines.on("change change:combination", updateTitle);
            if (statusSession.plan) {
                this.plan.set({"id":statusSession.plan});
                this.status.once("change:semester", function () {
                    this.plan.fetch().bind(this).then(function () {
                        this.plan.loadPlan(
                            this.status,
                            this.selectedDisciplines,
                            this.getHistory(),
                            statusSession.version || null
                        );
                        listen();
                    });
                }, this);
            } else {
                listen();
            }
            this.status.listenEvents();
        }
    });
});
