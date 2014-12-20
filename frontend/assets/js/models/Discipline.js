define("models/Discipline", ["underscore", "models/CachedModel","collections/Teams"], function(_, CachedModel, Teams) {
	"use strict";
	return CachedModel.extend({
		"defaults": {
			"id": -1,
			"code": "AAA0000",
			"name": "Sem nome",
			"_selected": false
		},
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
			this.teams.url = "/api/teams/?discipline="+this.id;
			this.set({
				"_selected": true
			});
			this.teamsRequest = this.teams.fetch().bind(this).then(function(){
				this.teams.map(function(model){
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
			this.teams.url = "/api/teams/?discipline="+this.id;
			this.set({
				"_selected": false
			});
			this.teamsRequest = this.teams.fetch().bind(this).then(function(){
				this.teams.map(function(model){
					model.set({
						"_selected": false
					});
				});
			});
			return this.teamsRequest;
		},
		"moveUp": function (){
			if(!this.collection) {
				throw "Cannot move up without a collection defined";
			}
			this.collection.moveUp(this);
		},
		"moveDown": function (){
			if(!this.collection) {
				throw "Cannot move down without a collection defined";
			}
			this.collection.moveDown(this);
		},
		"position": function(){
			if(!this.collection) {
				throw "Cannot get a position in the collection without a collection defined";
			}
			return this.collection.indexOf(this);
		},
		"isFirst": function(){
			return this.position() === 0;
		},
		"isLast": function(){
			if(!this.collection) {
				throw "Cannot get a position in the collection without a collection defined";
			}
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