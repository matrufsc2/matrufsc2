define("models/Semester", ["underscore", "models/CachedModel"], function (_, CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/semesters/",
        "defaults": {
            "id": -1,
            "name": "Sem nome"
        }
    });
});