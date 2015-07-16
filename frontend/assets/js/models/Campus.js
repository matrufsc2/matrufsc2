define("models/Campus", ["underscore", "models/CachedModel"], function(_, CachedModel) {
	"use strict";
	return CachedModel.extend({
		"urlRoot": "/api/campi",
		"defaults": {
			"id"          : -1,
			"name"        : "Sem nome"
		}
	});
});