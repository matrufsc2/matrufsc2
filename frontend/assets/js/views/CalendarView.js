define("views/CalendarView", ["views/BaseView", "templates", "underscore", "fastdom", "jquery"], function(BaseView, templates, _, fastdom, $){
	"use strict";
	var hours = ["07:30","08:20","09:10","10:10","11:00","13:30","14:20","15:10","16:20","17:10","18:30","19:20","20:20","21:10"];
	return BaseView.extend({
		"template": templates.calendar,
		"tagName": "table",
		"listen"   : {
			"change:combination collection": "render",
			"remove collection": "render"
		},
		"getTemplateData": function(){
			var events = this.collection.reduce(function(old, discipline){
				if(discipline.team) {
					old = old.concat(discipline.team.schedules.map(function(schedule){
						return {
							"title": discipline.get("code"),
							"color": discipline.get("_color"),
							"column": schedule.getStart().day(),
							"enabled": true,
							"rowStart": schedule.getStartRow(),
							"rowEnd": schedule.getEndRow()
						};
					}));
				}
				if(discipline.hoveredTeam) {
					old = old.concat(discipline.hoveredTeam.schedules.map(function(schedule){
						return {
							"title": discipline.get("code"),
							"color": discipline.get("_color"),
							"column": schedule.getStart().day(),
							"enabled": false,
							"rowStart": schedule.getStartRow(),
							"rowEnd": schedule.getEndRow()
						};
					}));
				}
				return old;
			},[]);
			var matrixEvents = {};
			for(var i=0; i<events.length; ++i) {
				var event = events[i];
				for(var row=event.rowStart; row <=event.rowEnd; ++row) {
					if(!matrixEvents[row]) {
						matrixEvents[row] = {};
					}
					matrixEvents[row][event.column] = {
						"title": event.title,
						"color": event.color,
						"enabled": event.enabled
					};
				}
			}
			return {
				"hours": hours,
				"events": matrixEvents
			};
		}
	});
});