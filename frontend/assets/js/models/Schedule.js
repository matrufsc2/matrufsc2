define("models/Schedule", ["models/CachedModel", "moment"], function(CachedModel, moment) {
	"use strict";
	var hours =  ["07:30","08:20","09:10","10:10","11:00","13:30","14:20","15:10","16:20","17:10","18:30","19:20","20:20","21:10"];
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
					"maximum"          : 22,
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
		"conflictsWith": function(schedule) {
			if (schedule.get("dayOfWeek") != this.get("dayOfWeek")) {
				return false;
			}
			var start1 = this.getStart();
			var start2 = schedule.getStart();
			var end1 = this.getEnd();
			var end2 = schedule.getEnd();
			return (start2.isBefore(end1) || start2.isSame(end1)) &&
				(end2.isAfter(start1) || end2.isSame(start1));
		},
		"getStart": function(){
			var start = moment();
			start.day(this.get("dayOfWeek"));
			start.hour(this.get("hourStart"));
			start.minute(this.get("minuteStart"));
			return start;
		},
		"getStartRow": function() {
			return hours.indexOf(this.getStart().format("HH:mm"));
		},
		"getEndRow": function() {
			return hours.indexOf(this.getStart().format("HH:mm"))+(this.get("numberOfLessons")-1);
		},
		"getEnd": function(){
			var hourString = hours[this.getEndRow()];
			var hourParts = hourString.split(":");
			var hour = parseInt(hourParts[0]);
			var minute = parseInt(hourParts[1]);
			var end = moment();
			end.day(this.get("dayOfWeek"));
			end.hour(hour);
			end.minute(minute);
			return end;
		}
	});
});