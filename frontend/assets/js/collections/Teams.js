define("collections/Teams", ["collections/CachedCollection", "models/Team"], function(CachedCollection, Team){
	"use strict";
	return CachedCollection.extend({
		"model": Team,
		"url": "/api/teams/"
	});
});