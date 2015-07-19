define("collections/Semesters", ["collections/CachedCollection", "models/Semester"], function (CachedCollection, Semester) {
    "use strict";
    return CachedCollection.extend({
        "model": Semester,
        "url": "/api/semesters/"
    });
});