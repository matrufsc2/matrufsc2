define("models/Status", ["models/CachedModel", "underscore"], function (CachedModel, _) {
    "use strict";
    return CachedModel.extend({
        "defaults": {
            "discipline": null,
            "campus": null,
            "semester": null,
            "editing": false,
            "plan": null,
            "version": null,
            "periods_allowed": ["morning", "afternoon", "night"],
            "days_of_week_allowed": [1, 2, 3, 4, 5, 6],
            "possibility": 1
        },
        "initialize": function (attributes, options) {
            CachedModel.prototype.initialize.call(this, attributes, options);
            this.campi = options.campi;
            this.semesters = options.semesters;
            this.campiRequest = null;
            this.semestersRequest = null;
        },
        "listenEvents": function () {
            this.listenTo(this.semesters, "sync", function () {
                if (this.semesters.length === 0 || this.get("semester") !== null || this.semesters.disposed ||
                    this.disposed) {
                    return;
                }
                this.semestersRequest = null;
                this.set({
                    "semester": this.semesters.at(0).id
                });
            });
            this.on("change:semester", function fetchCampi() {
                if (this.campi.isSyncing()) {
                    this.campi.once("syncStateChange", fetchCampi, this);
                    return;
                }
                var url = "/api/campi/?semester=" + this.get("semester");
                if (this.campi.url === url || this.campi.disposed || this.disposed) {
                    return;
                }
                this.set({
                    "campus": null
                }, {"silent": true});
                this.campi.reset();
                this.campi.url = url;
                this.campiRequest = this.campi.fetch({
                    "context": this
                }).then(_.bind(function () {
                    this.campi.map(function (campus) {
                        campus.semester = this.campi.get(this.get("semester"));
                    }, this);
                }, this));
            }, this);
            this.listenTo(this.campi, "sync", function () {
                if (this.campi.length === 0 || this.get("campus") !== null || this.campi.disposed || this.disposed) {
                    return;
                }
                this.campiRequest = null;
                this.set({
                    "campus": this.campi.at(0).id
                });
            });
            this.semestersRequest = this.semesters.fetch();
        }
    });
});