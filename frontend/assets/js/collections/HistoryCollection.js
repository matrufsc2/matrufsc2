define("collections/HistoryCollection", [
    "backbone.localStorage",
    "collections/BaseCollection",
    "models/HistoryItem"
], function(BackboneLocalStorage, BaseCollection, HistoryItem) {
    "use strict";
    return BaseCollection.extend({
        "model": HistoryItem,
        "localStorage": new BackboneLocalStorage("History"),
        "comparator": function(item1, item2) {
            return item1.id < item2.id;
        }
    });
});