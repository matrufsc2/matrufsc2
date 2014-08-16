define("collections/Teachers", ["collections/CachedCollection", "models/Teacher"], function(CachedCollection, Teacher){
	"use strict";
	return CachedCollection.extend({
		"model": Teacher
	});
});