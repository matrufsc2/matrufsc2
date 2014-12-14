define("collections/CachedCollection", ["collections/BaseCollection", "bluebird", "underscore"], function(BaseCollection, Promise, _) {
	"use strict";
	return BaseCollection.extend({
		"_cached": false,
		"fetch": function(options, callback){
			var collection = this;
			options = _.defaults(options || {}, {
				"cached": true
			});
			if(collection._cached  === false || options.cached === false) {
				collection._cached = BaseCollection.prototype.fetch.call(this, options, callback);
				collection._cached.then(function(){
					collection._cached = true;
				}, function(){
					collection._cached = false;
				});
			}
			if(collection._cached !== true) {
				return collection._cached.nodeify(callback);
			}
			return Promise.resolve().nodeify(callback);
		},
		"reset": function(){
			BaseCollection.prototype.reset.apply(this, _.toArray(arguments));
			this._cached = false;
		}
	});
});