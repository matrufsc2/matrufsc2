define("collections/Possibilities", ["collections/BaseCollection", "models/Possibility"], function(BaseCollection, Possibility) {
    "use strict";
    return BaseCollection.extend({
        "model": Possibility
    });
});