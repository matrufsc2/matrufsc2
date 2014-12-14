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
				if(this.semesters.length === 0 || this.get("semester") !== null  || this.semesters.disposed ||
					this.disposed) {
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
				var url = "/api/campi/?semester="+this.get("semester");
				if (this.campi.url === url || this.campi.disposed || this.disposed) {
					return;
				}
				this.set({
					"campus": null
				}, {"silent": true});
				this.campi.reset();
				this.campi.url = url;
				this.campi.fetch({
					"context": this
				}).then(function(){
					this.campi.map(function(campus){
						campus.semester = this.campi.get(this.get("semester"));
					}, this);
				});
			}, this);
			this.listenTo(this.campi, "sync", function(){
				if(this.campi.length === 0 || this.get("campus") !== null || this.campi.disposed || this.disposed) {
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
				var url = "/api/disciplines/?campus="+this.get("campus");
				if (!this.get("campus") || this.disciplines.url === url || this.disciplines.disposed || this.disposed) {
					return;
				}
				this.disciplines.reset();
				this.disciplines.url = url;
				this.disciplines.fetch({
					"context": this
				});
			}, this);
		}
	});
});