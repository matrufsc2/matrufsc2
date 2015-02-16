define("models/Discipline", [
    "underscore",
    "bluebird",
    "models/CachedModel",
    "collections/Teams"
], function(_, Promise, CachedModel, Teams) {
	"use strict";
	return CachedModel.extend({
		"defaults": {
			"id": -1,
			"code": "AAA0000",
			"name": "Sem nome",
			"_selected": false,
            "_custom": false
		},
		"urlRoot": "/api/disciplines/",
		"validator": {
			"type"     : "object",
			"required" : ["id", "code", "name"],
			"properties": {
				"id": {
					"type": "integer"
				},
				"code": {
					"type"    : "string",
					"pattern" : "[A-Z]{3}[0-9]{4}"
				},
				"name": {
					"type"      : "string",
					"minLength" : 3
				}
			}
		},
		"initialize": function(){
			this.teams = new Teams();
			this.teams.url = "/api/teams/?discipline="+this.id;
			this.teamsRequest = null;
			this.team = null;
			this.hoveredTeam = null;
			CachedModel.prototype.initialize.apply(this, _.toArray(arguments));
		},
		"isDisciplineEnabled": function(){
			return this.teams.reduce(function(old, team) {
				return old || team.get("_selected");
			}, false);
		},
		"select": function(){
			if (this.id === -1) {
				throw "Discipline ID not defined!";
			}
            if (this.get("_custom")) {
                this.teams.each(function(model){
					model.set({
						"_selected": true
					});
				});
                return Promise.resolve();
            }
			this.teams.url = "/api/teams/?discipline="+this.id;
            var discipline = this;
			this.teamsRequest = this.teams.fetch().then(function(){
				discipline.teams.map(function(model){
                    model.discipline = discipline;
					model.set({
						"_selected": true
					});
				});
			});
			return this.teamsRequest;
		},
		"unselect": function(){
			if (this.id === -1) {
				throw "Discipline ID not defined!";
			}
			this.collection.remove(this);
            if (this.get("_custom")) {
                this.teams.each(function(model){
					model.set({
						"_selected": false
					});
				});
                return Promise.resolve();
            }
			this.teams.url = "/api/teams/?discipline="+this.id;
			this.teamsRequest = this.teams.fetch().bind(this).then(function(){
				this.teams.each(function(model){
					model.set({
						"_selected": false
					});
				});
				this.teams.dispose();
				this.dispose();
			});
			return this.teamsRequest;
		},
		"moveUp": function (){
			this.collection.moveUp(this);
		},
		"moveDown": function (){
			this.collection.moveDown(this);
		},
		"position": function(){
			return this.collection.indexOf(this);
		},
		"isFirst": function(){
			return this.position() === 0;
		},
		"isLast": function(){
			return this.position() === this.collection.length - 1;
		},
		"dispose": function(){
			if (this.teamsRequest !== null) {
				this.teamsRequest.cancel();
			}
			CachedModel.prototype.dispose.call(this);
		}
	});
});