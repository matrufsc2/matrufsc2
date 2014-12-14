define("models/CachedModel", ["models/BaseModel", "bluebird", "underscore"], function(BaseModel, Promise, _) {
	"use strict";
	return BaseModel.extend({
		"_cached": false,
		"fetch": function(options, callback){
			var model = this;
			options = _.defaults(options || {}, {
				"cached": true
			});
			if(model._cached  === false || options.cached === false) {
				model._cached = BaseModel.prototype.fetch.call(this, options);
				model._cached.then(function(){
					model._cached = true;
				}, function(){
					model._cached = false;
				});
				return model._cached.nodeify(callback);
			}
			if(model._cached !== true) {
				return model._cached.nodeify(callback);
			}
			return Promise.resolve().nodeify(callback);
		},
		"reset": function(){
			this._cached = false;
			BaseModel.prototype.reset.apply(this, _.toArray(arguments));
		}
	});
});