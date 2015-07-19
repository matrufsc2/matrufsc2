define("models/QuestionsGroup", ["underscore", "models/CachedModel"], function (_, CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/questions-groups",
        "eachQuestion": function (callback) {
            return _.each(this.get("questions") || [], callback);
        }
    });
});