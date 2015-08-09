define("models/Post", ["models/CachedModel"], function (CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/posts/"
    });
});