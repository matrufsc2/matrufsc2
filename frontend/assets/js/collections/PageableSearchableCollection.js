define("collections/PageableSearchableCollection", [
    "collections/PageableCollection",
    "collections/SearchableCollection"
], function (PageableCollection, SearchableCollection) {
    "use strict";
    return SearchableCollection.extend(PageableCollection).extend({
        "parse": PageableCollection.prototype.parse,
        "fetch": function (options) {
            options = options || {};
            options.data = options.data || {};
            if (this.query !== null) {
                options.data.q = this.query;
            }
            return PageableCollection.prototype.fetch.call(this, options);
        }
    })
});