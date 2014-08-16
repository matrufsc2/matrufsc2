define("collections/Campi", ["collections/CachedCollection", "models/Campus"], function(CachedCollection, Campus){
	"use strict";
	return CachedCollection.extend({
		"model": Campus,
		"url": "/api/campi/"
	});
});