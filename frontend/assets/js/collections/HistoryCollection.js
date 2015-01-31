define("collections/HistoryCollection", [
    "collections/BaseCollection",
    "models/HistoryItem"
], function(BaseCollection, HistoryItem) {
    "use strict";
    return BaseCollection.extend({
        "model": HistoryItem,
        "comparator": function(item1, item2) {
            return item1.id < item2.id;
        }
    });
});