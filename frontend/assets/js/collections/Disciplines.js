define("collections/Disciplines", ["collections/CachedCollection", "models/Discipline"], function(CachedCollection, Discipline){
	"use strict";
	return CachedCollection.extend({
		"model": Discipline,
		"url": "/api/disciplines",
		"move": function(model, delta) {
			var index = this.indexOf(model);
			if ((delta < 0 && index+delta >= 0) || (delta > 0 && index+delta < this.length)) {
				this.moveTo(model, index+delta);
			}
		},
		"moveTo": function(model, index) {
			this.remove(model);
			this.add(model, {"at": index});
		},
		"moveUp": function(model) {
			this.move(model, -1);
		},
		"moveDown": function(model) {
			this.move(model, 1);
		}
	});
});