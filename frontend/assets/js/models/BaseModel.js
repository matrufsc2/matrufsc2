define("models/BaseModel", ["underscore", "chaplin", "tv4", "oboe", "bluebird"], function(_, Chaplin, tv4, oboe, Promise) {
	"use strict";
	var BaseModel = Chaplin.Model.extend({
		"validator": {
			"type": "object"
		},
		"initialize": function(){
			this.trigger("initialize");
		},
		"validate": function(){
			var result = tv4.validateResult(this.toJSON(), _.result(this, "validator"));
			if (result.missing.length > 0){
				throw new Error("Missing schemas detected. Please fix it to do perfect validation: "+result.missing.join(","));
			}
			if (!result.valid) {
				return result.error;
			}
		},
		"fetch": function(options, callback){
			// Do the request using OboeJS, which allow progressive loading of the model.
			options = _.defaults(options || {}, {
				"cached": true,
				"url": _.result(this, "url"),
				"type": "GET",
				"headers": null,
				"body": null
			});
			var context = options.context || this;
			var model = this;
			return (new Promise(function(resolve, reject) {
				model.beginSync();
				var req = oboe({
					"url": _.result(model, "url"),
					"method": options.type,
					"headers": options.headers,
					"cached": options.cache,
					"body": options.data
				});
				req.node("[*]", function(){
					// Progressive set when a node is fully loaded.
					model.set(req.root(), options);
				});
				req.done(function(){
					model.set(req.root(), options);
					model.trigger("sync", model, req.root(), options);
					resolve();
				});
				req.fail(reject);
			}))
			.bind(context)
			.nodeify(callback)
			.then(function(){
				model.finishSync();
			}, function(){
				model.unsync();
			});
		}
	});
	_.extend(BaseModel.prototype, Chaplin.SyncMachine);
	return BaseModel;
});