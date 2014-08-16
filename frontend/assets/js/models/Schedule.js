define("models/Schedule", ["models/CachedModel", "moment"], function(CachedModel, moment) {
	"use strict";
	return CachedModel.extend({
		"defaults": {
			"id": -1,
			"hourStart": 0,
			"minuteStart": 0,
			"numberOfLessons": 0,
			"dayOfWeek": 2,
			"room": "AUX/ALOCAR"
		},
		"validator": {
			"type": "object",
			"required": ["id", "hourStart", "minuteStart", "numberOfLessons", "dayOfWeek", "room"],
			"properties": {
				"id": {
					"type": "integer"
				},
				"hourStart": {
					"type"             : "integer",
					"minimum"          : 0,
					"exclusiveMinimum" : false,
					"maximum"          : 23,
					"exclusiveMaximum" : false
				},
				"minuteStart": {
					"type"             : "integer",
					"minimum"          : 0,
					"exclusiveMinimum" : false,
					"maximum"          : 59,
					"exclusiveMaximum" : false
				},
				"numberOfLessons": {
					"type"             : "integer",
					"minimum"          : 0,
					"exclusiveMinimum" : false,
					"maximum"          : 14,
					"exclusiveMaximum" : false
				},
				"dayOfWeek": {
					"type"             : "integer",
					"minimum"          : 2, // Segunda-feira
					"exclusiveMinimum" : false,
					"maximum"          : 6, // Sexta-feira
					"exclusiveMaximum" : false
				},
				"room": {
					"type"          : "string",
					"minimumLength" : 5,
					"maximumLength" : 11
				}
			}
		},
		"conflictsWith": function(){
			return false;
		},
		"getStart": function(){
			var start = moment();
			start.day(this.get("dayOfWeek"));
			start.hour(this.get("hourStart"));
			start.minute(this.get("minuteStart"));
			return start;
		}
	});
});