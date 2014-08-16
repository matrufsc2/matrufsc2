define("collections/BaseCollection", ["underscore", "chaplin", "oboe", "bluebird"], function(_, Chaplin, oboe, Promise) {
	"use strict";
	var BaseCollection = Chaplin.Collection.extend({
		"fetch": function(options, callback){
			// Do the request using OboeJS, which allow progressive loading of the collection.
			options = _.defaults(options || {}, {
				"cached": true,
				"url": _.result(this, "url"),
				"type": "GET",
				"headers": null,
				"body": null
			});
			var context = options.context || this;
			var collection = this;
			return (new Promise(function(resolve, reject) {
				collection.beginSync();
				var req = oboe({
					"url": _.result(collection, "url"),
					"method": options.type,
					"headers": options.headers,
					"cached": options.cache !== false ? true : false,
					"body": options.data
				});
				req.node("[*]", function(){
					// Progressive set.
					collection.set(_.filter(req.root(), function(model){
						return _.has(model, (new collection.model(model)).idAttribute);
					}));
				});
				req.done(function(){
					collection.set(_.filter(req.root(), function(model){
						// Allow only models with an ID defined to be set-ed.
						return _.has(model, (new collection.model(model)).idAttribute);
					}));
					collection.trigger("sync", collection, req.root(), options);
					resolve();
				});
				req.fail(function(err){
					reject(err.thrown);
				});
			}))
			.bind(context)
			.nodeify(callback)
			.then(function(){
				collection.finishSync();
			}, function(){
				collection.unsync();
			});;
		}
	});
	_.extend(BaseCollection.prototype, Chaplin.SyncMachine);
	return BaseCollection;
});