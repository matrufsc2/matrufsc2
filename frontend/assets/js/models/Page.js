define("models/Page", ["models/CachedModel"], function (CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/pages"
    });
});