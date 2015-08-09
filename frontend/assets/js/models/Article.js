define("models/Article", ["models/CachedModel"], function (CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/articles/"
    });
});