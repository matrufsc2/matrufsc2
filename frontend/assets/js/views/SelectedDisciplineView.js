define("views/SelectedDisciplineView", [
		"templates",
		"jquery",
		"underscore",
		"views/BaseView"
		], function(templates, $, _, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.selectedDiscipline,
		"tagName": "tr",
		"events": {
			"click .icon-delete": "unselect",
			"click .selectedDiscipline": "updateTeams",
			"click .icon-up": "moveUp",
			"click .icon-down": "moveDown",
			"click td:lt(4)": "select"
		},
		"initialize": function(options) {
			this.status = options.status;
			this.blinkId = null;
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
			this.model.collection.updateCombinations();
			this.model.collection.trigger("change:combination");
			e.preventDefault();
		},
		"unselect": function(e){
			this.model.unselect();
			this.status.set({
				"discipline": null
			});
			e.preventDefault();
		},
		"updateTeams": function(e){
			var isEnabled = this.$(e.currentTarget).is(":checked");
			this.model.teams.each(function(team) {
				team.set({
					"_selected": isEnabled
				});
			});
			this.model.collection.updateCombinations();
			this.model.collection.trigger("change:combination");
			this.render();
			this.status.trigger("change:discipline");
		},
		"moveUp": function(e){
			this.model.moveUp();
			e.preventDefault();
		},
		"moveDown": function(e){
			this.model.moveDown();
			e.preventDefault();
		},
		"render": function(){
			BaseView.prototype.render.apply(this, []);
			if (this.model.has("_title") && this.blinkId === null) {
				this.blinkId = _.delay(function blink(view, status){
					if (!view.model.has("_title")) {
						view.$(".title").css("opacity", 1);
						view.blinkId = null;
						return;
					}
					var opacity = view.$(".title").css("opacity");
					view.$(".title").animate({
						"opacity": status ? 1 : 0.5
					}, 400, 'swing', function(){
						view.blinkId = _.delay(blink, 500, view, !status);
					});
				}, 500, this, false);
			}
			this.$el.css("background-color", this.model.get("_color"));
		}
	});
});