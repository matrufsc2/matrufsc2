define("models/BaseModel", ["underscore", "chaplin", "es6-promise"], function(_, Chaplin) {
	"use strict";
	var BaseModel = Chaplin.Model.extend({
		"validator": {
			"type": "object"
		},
		"initialize": function(){
			this.trigger("initialize");
		},
		"fetch": function(options, callback){
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
			var xhr;
			return (new Promise(function(resolve, reject) {
				model.beginSync();
				options.success = resolve;
				options.error = reject;
				xhr = Chaplin.Model.prototype.fetch.call(model, options);
			}))
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