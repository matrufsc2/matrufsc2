define("views/SelectedDisciplineView", [
		"templates",
		"jquery",
		"fastdom",
		"views/BaseView"
		], function(templates, $, fastdom, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.selectedDiscipline,
		"tagName": "tr",
		"events": {
			"click .icon-delete": "unselect",
			"click .icon-up": "moveUp",
			"click .icon-down": "moveDown",
			"click td:lt(4)": "select",
			"change model": "render"
		},
		"initialize": function(options) {
			this.status = options.status;
			this.blinkId = null;
			this.blinkOn = false;
			this.listenTo(this.model.teams, "syncStateChange", this.render);
		},
		"getTemplateData": function(){
			return {
				"discipline": this.model
			};
		},
		"select": function(e){
			this.status.set({
				"discipline": this.model.id
			});
			e.preventDefault();
		},
		"unselect": function(e){
			this.model.unselect();
			this.status.set({
				"discipline": null
			});
			e.preventDefault();
		},
		"moveUp": function(e){
			this.model.moveUp();
			e.preventDefault();
		},
		"moveDown": function(e){
			this.model.moveDown();
			e.preventDefault();
		},
		"dispose": function(){
			var view = this;
			this.$el.animate({
				"opacity": 0
			}, 400, function(){
				BaseView.prototype.dispose.apply(view, []);
			});
		},
		"startBlink": function() {
			if (this.blinkId !== null) {
				return;
			}
			var view = this;
			this.blinkId = setTimeout(function blink(){
				view.blinkOn = !view.blinkOn;
				view.$el.animate({
					"opacity": view.blinkOn ? 1 : 0.5
				}, 500, function(){
					view.blinkId = setTimeout(blink, 100);
				})
			}, 500);
		},
		"stopBlink": function() {
			if (this.blinkId === null) {
				return;
			}
			clearTimeout(this.blinkId);
			this.blinkId = null;
			this.$el.animate({
				"opacity": 1
			}, 500);
		},
		"render": function(){
			BaseView.prototype.render.apply(this, []);
			if (this.model.get("_blink")) {
				this.startBlink();
			} else {
				this.stopBlink();
			}
			fastdom.write(function(){
				this.$el.css("background-color", this.model.get("_color"));
			}, this);
		}
	});
});