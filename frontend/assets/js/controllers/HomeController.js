define("controllers/HomeController", [
    "underscore",
    "backbone",
    "chaplin",
    "collections/Campi",
    "collections/Semesters",
    "collections/SelectedDisciplines",
    "collections/HistoryCollection",
    "collections/Possibilities",
    "controllers/BaseController",
    "models/Status",
    "models/Discipline",
    "models/Plan",
    "views/HeaderView",
    "views/HomeView"
], function (_,
             Backbone,
             Chaplin,
             Campi,
             Semesters,
             SelectedDisciplines,
             HistoryCollection,
             Possibilities,
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
            this.possibilitiesCollection = null;
            this.plan = new Plan();
            this.campi = new Campi();
            this.semesters = new Semesters();
            this.possibilities = new Possibilities([{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]);
            this.history = new HistoryCollection();
            this.status = new Status({}, {
                "campi": this.campi,
                "semesters": this.semesters
            });
        },
        "getHeader": function () {
            if (!this.header || this.header.disposed) {
                this.header = new HeaderView({
                    "history": this.history,
                    "possibilities": this.possibilities,
                    "status": this.status,
                    "route": this.route,
                    "user": this.user
                });
            }
            return this.header;
        },
        "index": function (params, metadata, request) {
            this.adjustTitle("");
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
                "history": this.history,
                "possibilities": this.possibilities,
                "plan": this.plan,
                "user": this.user
            });
            var statusSessionKeys = [
                "plan",
                "version",
                "possibility"
            ];
            var statusSession = _.pick(request.query, statusSessionKeys) || {};
            var listen = _.bind(function () {
                this.status.on("change:possibility", function () {
                    var previousPossibility = this.status.previous("possibility");
                    previousPossibility = this.possibilities.get(previousPossibility);
                    if (previousPossibility) {
                        previousPossibility.savePossibility(this.status, this.selectedDisciplines);
                    }
                    var possibility = this.status.get("possibility");
                    possibility = possibility || 1;
                    possibility = parseInt(possibility);
                    if (!_.isNumber(possibility) || _.isNaN(possibility)) {
                        alert("Plano inválido! Iremos carregar o plano 1, portanto.");
                        return this.status.set({"possibility": 1});
                    }
                    possibility = this.possibilities.get(possibility);
                    if (!possibility) {
                        return alert("Plano não encontrado!");
                    }
                    if (previousPossibility && !!previousPossibility.get("selectedDisciplines").length && !possibility.get("selectedDisciplines").length &&
                        confirm("Você deseja copiar o plano "+previousPossibility.id+" para o plano "+possibility.id+"?")) {
                        possibility.set(_.omit(previousPossibility.toJSON(), 'id'));
                    } else if (!possibility.get("selectedDisciplines").length && this.semesters.length > 0 && this.campi.length > 0) {
                        possibility.set({
                            "semester": this.semesters.at(0).id,
                            "campus": this.campi.at(0).id
                        });
                    }
                    possibility.loadPossibility(this.status, this.selectedDisciplines).bind(this).catch(function (err) {
                        if (_.isString(err)) {
                            var error_container = this.view.$("#error-discipline");
                            error_container.find("p").html(err);
                            error_container.foundation("reveal", "open");
                        }
                    });
                }, this);
                this.status.on("change:version", function () {
                    this.plan.loadPlan(
                        this.status,
                        this.selectedDisciplines,
                        this.possibilities,
                        this.history,
                        this.status.get("version"),
                        this.status.get("possibility")
                    ).bind(this).catch(function (err) {
                            if (_.isString(err)) {
                                var error_container = this.view.$("#error-discipline");
                                error_container.find("p").html(err);
                                error_container.foundation("reveal", "open");
                            }
                        });
                }, this);
                var updateURL = function(){
                    var url = Chaplin.utils.reverse("Home#index", {
                        "plan": this.plan.id,
                        "version": this.status.get("version"),
                        "possibility": this.status.get("possibility")
                    });
                    Backbone.history.navigate(url, {"trigger": false, "replace": false});
                };
                this.plan.on("change:id", updateURL, this);
                this.status.on("change:version change:possibility", updateURL, this);
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
                this.plan.set({"id": statusSession.plan});
                this.status.once("change:semester", function () {
                    this.plan.fetch().bind(this).then(function () {
                        return this.plan.loadPlan(
                            this.status,
                            this.selectedDisciplines,
                            this.possibilities,
                            this.history,
                            statusSession.version,
                            statusSession.possibility || 1
                        );
                    }).then(function () {
                        this.status.set({
                            "version": statusSession.version,
                            "possibility": parseInt(statusSession.possibility) || 1
                        }, {"silent": true});
                        this.getHeader().render();
                        listen();
                    }, function (err) {
                        if (_.isString(err)) {
                            var error_container = this.view.$("#error-discipline");
                            error_container.find("p").html(err);
                            error_container.foundation("reveal", "open");
                        }
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
