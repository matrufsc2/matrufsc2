define("models/Team", ["underscore", "models/CachedModel", "collections/Teachers", "collections/Schedules"], function(_, CachedModel, Teachers, Schedules) {
	"use strict";
	return CachedModel.extend({
		"defaults": {
			"id"   : -1,
			"code": "AAAA-000",
			"vacancies_offered": 0,
			"vacancies_filled": 0,
			"_selected": false
		},
		"validator": {
			"type"     : "object",
			"required" : ["id", "code", "teachers", "schedules", "vacancies_offered", "vacancies_filled"],
			"properties": {
				"id": {
					"type": "integer"
				},
				"code": {
					"type"      : "string",
					"minLength" : 3
				},
				"teachers": {
					"type": "array",
					"items": {
						"type"     : "object",
						"required" : ["id", "name"],
						"properties": {
							"id": {
								"type"    : "integer",
								"minimum" : 0
							},
							"name": {
								"type"          : "string",
								"minimumLength" : 3
							}
						}
					}
				},
				"schedules": {
					"type": "array",
					"items": {
						"type": "object",
						"required": ["id", "hourStart", "minuteStart", "numberOfClasses", "dayOfWeek", "room"],
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
							"numberOfClasses": {
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
					}
				},
				"vacancies_offered": {
					"type": "integer"
				},
				"vacancies_filled": {
					"type": "integer"
				}
			}
		},
		"initialize": function(){
			this.teachers = new Teachers();
			this.schedules = new Schedules();
			this.on("change:teachers initialize", function(){
				var teachers = this.get("teachers") || [];
				this.teachers.set(teachers, {"reset": true});
			}, this);
			this.on("change:schedules initialize", function(){
				var schedules = this.get("schedules") || [];
				this.schedules.set(schedules, {"reset": true});
			}, this);
			CachedModel.prototype.initialize.apply(this, _.toArray(arguments));
		},
		"getNumberOfLessons": function(){
			return this.schedules.reduce(function(total, schedule) {
				return total + schedule.get("numberOfLessons");
			}, 0);
		}
	});
});