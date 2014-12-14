define("models/BaseModel", ["underscore", "chaplin", "tv4", "bluebird"], function(_, Chaplin, tv4, Promise) {
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
			var oldSuccess = options.success;
			var oldError = options.error;
			return (new Promise(function(resolve, reject) {
				model.beginSync();
				options.success = resolve;
				options.error = reject;
				Chaplin.Model.prototype.fetch.call(model, options);
			}))
			.bind(context)
			.nodeify(callback)
			.then(function(){
				model.finishSync();
				if (_.isFunction(oldSuccess)) {
					oldSuccess.apply(context, _.toArray(arguments));
				}
			}, function(){
				model.unsync();
				if (_.isFunction(oldError)) {
					oldError.apply(context, _.toArray(arguments));
				}
			});
		}
	});
	_.extend(BaseModel.prototype, Chaplin.SyncMachine);
	return BaseModel;
});