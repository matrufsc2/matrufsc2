define("views/CalendarView", [
    "views/BaseView",
    "templates",
    "jquery",
    "underscore",
    "models/Schedule"
], function(BaseView, templates, $, _, Schedule){
	"use strict";
	var hours = ["07:30","08:20","09:10","10:10","11:00","13:30","14:20","15:10","16:20","17:10","18:30","19:20","20:20","21:10"];
	var daysOfWeek = [null, 1, 2, 3, 4, 5, 6, null];
	return BaseView.extend({
		"template": templates.calendar,
		"tagName": "table",
		"listen"   : {
			"change:combination collection": "render",
			"remove collection": "render"
		},
        "events": {
            "mousedown tbody td": "saveSchedule",
            "contextmenu tbody td": "disableContextMenu",
            "mouseover tbody td ": "colorizeSchedule"
        },
        "initialize": function(options) {
            BaseView.prototype.initialize.call(this, options);
            this.actualSchedule = null;
            this.status = options.status;
        },
        "fromTeamToEvents": function(team, enabled, custom){
            if (!team) {
                return [];
            }
            return team.schedules.map(function(schedule){
                return {
                    "title": team.discipline.get("code"),
                    "color": this.actualSchedule && schedule.id === this.actualSchedule.id ? "black" : team.discipline.get("_color"),
                    "fontColor": this.actualSchedule && schedule.id === this.actualSchedule.id ? "white" : "black",
                    "name": (custom ? "Clique para editar (ou clique com o botão direito do mouse para apagar)" :
                        team.discipline.get("name")),
                    "column": daysOfWeek[schedule.getStart().day()],
                    "enabled": enabled,
                    "rowStart": schedule.getStartRow(),
                    "rowEnd": schedule.getEndRow(),
                    "custom": custom,
                    "schedule": schedule
                };
            }, this);
        },
		"getTemplateData": function(){
            var events = this.collection.reduce(function(old, discipline){
                var events = [];
                if (this.status.get("editing") === true && this.status.get("discipline") === discipline.id) {
                    events = this.fromTeamToEvents(discipline.team, true, true);
                } else {
                    if(discipline.team) {
                        events = this.fromTeamToEvents(discipline.team, true);
                    }
                    if(discipline.hoveredTeam) {
                        events = events.concat(this.fromTeamToEvents(discipline.hoveredTeam, false));
                    }
                }
                if (this.status.get("editing") === true) {
                    if (this.status.get("discipline") === discipline.id) {
                        old = old.concat(events);
                    } else {
                        old = events.concat(old);
                    }
                } else {
                    old = old.concat(events);
                }
                return old;
            },[], this);

			var matrixEvents = {};
			for(var i=0; i<events.length; ++i) {
				var event = events[i];
				for(var row=event.rowStart; row <=event.rowEnd; ++row) {
					if(!matrixEvents[row]) {
						matrixEvents[row] = {};
					}
                    if (this.collection.isConflicting()) {
                        if (!!matrixEvents[row][event.column]) {
                            matrixEvents[row][event.column] = {
                                "title": "CONFLITO",
                                "name": "Conflito entre '"+matrixEvents[row][event.column].name+"' e '"+event.name+"'",
                                "color": "red",
                                "fontColor": event.fontColor,
                                "enabled": true,
                                "schedule_point": null,
                                "schedule": null,
                                "custom": false
                            };
                            continue;
                        }
                    }
					matrixEvents[row][event.column] = {
						"title": event.title,
						"name": event.name,
						"color": event.color,
						"enabled": event.enabled,
                        "schedule": null,
                        "fontColor": event.fontColor,
                        "custom": event.custom
					};
                    if(event.custom) {
                        matrixEvents[row][event.column].schedule_point_margin = row - event.rowStart;
                        matrixEvents[row][event.column].schedule = event.schedule.id;
                    }
				}
			}
			return {
				"hours": hours,
				"events": matrixEvents,
                "default_title": "",
                "default_name": this.status.get("editing") ? "Clique para cadastrar um horario aqui": ""
			};
		},
        "changeSchedule": function(e, permanent){
            var  el, column, row, model, dayOfWeek, schedule, hour;
            el = $(e.currentTarget);
            column = el.data("column");
            row = el.data("row");
            model = this.collection.get(this.status.get("discipline"));
            window.m = model;
            if (!model || this.status.get("editing") === false) {
                return;
            }
            if (!model.team) {
                return alert("Selecione uma turma para editar!");
            }
            if (column === undefined || row === undefined) {
                return;
            }
            hour = hours[row].split(":");
            dayOfWeek = daysOfWeek.indexOf(column) + 1;
            schedule = model.team.schedules.get(el.data("schedule"));
            if (permanent !== false) {
                if (this.actualSchedule) {
                    this.actualSchedule = null;
                    this.render();
                }
                else if (schedule) {
                    if (e.which === 3) {
                        e.preventDefault();
                        model.team.schedules.remove(schedule);
                    } else {
                        this.actualSchedule = schedule;
                    }
                    this.render();
                } else {
                    var actualSchedule = new Schedule();
                    actualSchedule.collection = model.team.schedules;
                    actualSchedule.set({
                        "id": _.uniqueId("schedule"),
                        "dayOfWeek": dayOfWeek,
                        "hourStart": parseInt(hour[0]),
                        "minuteStart": parseInt(hour[1]),
                        "numberOfLessons": 1
                    });
                    model.team.schedules.add(actualSchedule);
                    this.render();
                }
            } else if (this.actualSchedule && (this.actualSchedule.getStartRow() !== row || this.actualSchedule.get("dayOfWeek") !== dayOfWeek)) {
                this.actualSchedule.set({
                    "hourStart": parseInt(hour[0]),
                    "minuteStart": parseInt(hour[1]),
                    "dayOfWeek": dayOfWeek
                });
                this.render();
            }
        },
        "colorizeSchedule": function(e) {
            if (this.actualSchedule) {
                return this.changeSchedule(e, false);
            }
        },
        "saveSchedule": function(e){
            return this.changeSchedule(e, true);
        },
        "disableContextMenu": function(){
            return false;
        }
	});
});