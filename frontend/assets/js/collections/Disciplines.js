define("collections/Disciplines", ["collections/CachedCollection", "models/Discipline"], function(CachedCollection, Discipline){
	"use strict";
	return CachedCollection.extend({
		"model": Discipline,
		"url": "/api/disciplines",
		"move": function(model, delta) {
			var index = this.indexOf(model);
			if ((delta < 0 && index > 0) || (delta > 0 && index < (this.length-1))) {
				this.moveTo(model, index+delta);//Moves the actual model
			}
		},
		"moveTo": function(model, index) {
			this.remove(model, {"silent": true});
			model.collection = this;
			this.add(model, {"at": index, "silent": true});
			this.trigger("sort");
		},
		"moveUp": function(model) {
			this.move(model, -1);
		},
		"moveDown": function(model) {
			this.move(model, 1);
		}
	});
});