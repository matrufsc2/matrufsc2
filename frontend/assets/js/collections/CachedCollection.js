define("collections/CachedCollection", ["collections/BaseCollection", "underscore"], function (BaseCollection, _) {
    "use strict";
    return BaseCollection.extend({
        "_cached": false,
        "fetch": function (options) {
            var collection = this;
            options = _.defaults(options || {}, {
                "cached": true
            });
            if (collection._cached === false || options.cached === false) {
                collection._cached = BaseCollection.prototype.fetch.call(this, options);
                collection._cached.then(undefined, function () {
                    collection._cached = false;
                });
            }
            if (_.isFunction(options.success)) {
                collection._cached.then(function () {
                    options.success.apply(collection, _.toArray(arguments));
                });
            }
            if (_.isFunction(options.error)) {
                collection._cached.then(undefined, function () {
                    options.error.apply(collection, _.toArray(arguments));
                });
            }
            return collection._cached;
        },
        "reset": function () {
            BaseCollection.prototype.reset.apply(this, _.toArray(arguments));
            this._cached = false;
        }
    });
});