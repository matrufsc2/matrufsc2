define("models/Semester", ["underscore", "models/CachedModel"], function(_, CachedModel) {
	"use strict";
	return CachedModel.extend({
		"validator": {
			"type"       : "object",
			"required"   : ["id", "name"],
			"properties" : {
				"id"   : {
					"type" : "integer"
				},
				"name" : {
					"type"      : "string",
					"pattern"   : /(\d{4})-(\d{1})/
				}
			}
		}
	});
});