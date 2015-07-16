define("models/Category", ["models/CachedModel"], function(CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/categories/"
    });
});