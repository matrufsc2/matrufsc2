define("models/Status", ["models/CachedModel"], function(CachedModel){
	"use strict";
	return CachedModel.extend({
		"defaults": {
			"discipline": null,
			"campus": null,
			"semester": null
		},
		"initialize": function(attributes, options) {
			CachedModel.prototype.initialize.call(this, attributes, options);
			this.disciplines = options.disciplines;
			this.campi = options.campi;
			this.semesters = options.semesters;
			this.listenEvents();
		},
		"listenEvents": function() {
			this.listenTo(this.semesters, "sync", function(){
				if(this.semesters.length === 0 || this.get("semester") !== null) {
					return;
				}
				this.set({
					"semester": this.semesters.at(0).id
				});
			});
			this.on("change:semester", function fetchCampi(){
				if(this.campi.isSyncing()) {
					return this.campi.once("syncStateChange", fetchCampi, this);
				}
				this.set({
					"campus": null
				});
				this.campi.reset();
				this.campi.url = "/api/campi/?semester="+this.get("semester");
				this.campi.fetch({
					"context": this
				}).then(function(){
					this.campi.map(function(campus){
						campus.semester = this.campi.get(this.get("semester"));
					}, this);
				});
			}, this);
			this.listenTo(this.campi, "sync", function(){
				if(this.campi.length === 0 || this.get("campus") !== null) {
					return;
				}
				this.set({
					"campus": this.campi.at(0).id
				});
			});
			this.on("change:campus", function fetchDisciplines(){
				if(this.disciplines.isSyncing()) {
					return this.disciplines.once("syncStateChange", fetchDisciplines, this);
				}
				this.disciplines.reset();
				this.disciplines.url = "/api/disciplines/?campus="+this.get("campus");
				this.disciplines.fetch({
					"context": this
				});
			}, this);
		}
	});
});