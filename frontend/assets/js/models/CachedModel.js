define("models/CachedModel", ["models/BaseModel", "underscore", "es6-promise"], function (BaseModel, _) {
    "use strict";
    return BaseModel.extend({
        "_cached": false,
        "fetch": function (options, callback) {
            var model = this;
            options = _.defaults(options || {}, {
                "cached": true
            });
            if (model._cached === false || options.cached === false) {
                model._cached = BaseModel.prototype.fetch.call(this, options);
                model._cached.then(undefined, function () {
                    model._cached = false;
                });
            }
            if (_.isFunction(options.success)) {
                model._cached.then(function () {
                    options.success.apply(this, _.toArray(arguments));
                });
            }
            if (_.isFunction(options.error)) {
                model._cached.then(undefined, function () {
                    options.error.apply(this, _.toArray(arguments));
                });
            }
            return model._cached;
        },
        "reset": function () {
            this._cached = false;
            BaseModel.prototype.reset.apply(this, _.toArray(arguments));
        }
    });
});