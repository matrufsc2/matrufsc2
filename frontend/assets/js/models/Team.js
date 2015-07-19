define("models/Team", ["underscore", "models/CachedModel", "collections/Teachers", "collections/Schedules"], function (_, CachedModel, Teachers, Schedules) {
    "use strict";
    return CachedModel.extend({
        "defaults": {
            "id": -1,
            "code": "AAAA-000",
            "vacancies_offered": 0,
            "vacancies_filled": 0,
            "_selected": false
        },
        "initialize": function () {
            this.teachers = new Teachers();
            this.schedules = new Schedules();
            this.on("change:teachers initialize", function () {
                var teachers = this.get("teachers") || [];
                this.teachers.set(teachers, {"reset": true});
            }, this);
            this.on("change:schedules initialize", function () {
                var schedules = this.get("schedules") || [];
                this.schedules.set(schedules, {"reset": true});
            }, this);
            CachedModel.prototype.initialize.apply(this, _.toArray(arguments));
        },
        "getNumberOfLessons": function () {
            return this.schedules.getNumberOfLessons();
        }
    });
});