define("models/Campus", ["models/CachedModel"], function (CachedModel) {
    "use strict";
    return CachedModel.extend({
        "urlRoot": "/api/campi",
        "defaults": {
            "id": -1,
            "name": "Sem nome"
        }
    });
});