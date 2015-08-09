define("models/Section", ["models/CachedModel"], function (CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/sections/"
    });
});