define("models/Campus", ["underscore", "models/CachedModel","collections/Disciplines"], function(_, CachedModel, Disciplines) {
	"use strict";
	return CachedModel.extend({
		"urlRoot": "/api/campi",
		"defaults": {
			"id"          : -1,
			"name"        : "Sem nome"
		},
		"validator": {
			"type"       : "object",
			"required"   : ["id", "name"],
			"properties" : {
				"id"   : {
					"type" : "integer"
				},
				"name" : {
					"type"      : "string",
					"minLength" : 3
				}
			}
		}
	});
});