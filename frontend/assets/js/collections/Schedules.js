define("collections/Schedules", ["collections/CachedCollection", "models/Schedule"], function(CachedCollection, Schedule){
	"use strict";
	return CachedCollection.extend({
		"model": Schedule
	});
});