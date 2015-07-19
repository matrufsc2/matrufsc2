define("collections/Plans", ["collections/BaseCollection", "models/Plan"], function (BaseCollection, Plan) {
    "use strict";
    return BaseCollection.extend({
        "model": Plan
    });
});