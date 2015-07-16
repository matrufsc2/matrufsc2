define("models/Teacher", ["underscore", "models/CachedModel"], function(_, CachedModel) {
	"use strict";
	return CachedModel.extend({
		"defaults": {
			"id": -1,
			"name": "Sem nome"
		}
	});
});