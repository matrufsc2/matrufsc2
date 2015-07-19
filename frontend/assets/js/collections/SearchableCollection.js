define("collections/SearchableCollection", ["chaplin"], function (Chaplin) {
    "use strict";
    return Chaplin.Collection.extend({
        "query": null,
        "fetch": function (options) {
            options = options || {};
            options.data = options.data || {};
            if (this.query !== null) {
                options.data.q = this.query;
            }
            return this.__super__.fetch(options);
        },
        "search": function (query) {
            this.query = query;
            this.fetch();
        },
        "getQuery": function () {
            return this.query;
        }
    });
});