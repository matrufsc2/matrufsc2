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
			"click td:lt(4)": "select"
		},
		"initialize": function(options) {
			this.status = options.status;
		},
		"getTemplateData": function(){
			return {
				"discipline": this.model
			};
		},
		"select": function(){
			this.status.set({
				"discipline": this.model.id
			});
		},
		"unselect": function(){
			this.model.unselect();
			this.status.set({
				"discipline": null
			});
		},
		"moveUp": function(){
			this.model.moveUp();
		},
		"moveDown": function(){
			this.model.moveDown();
		},
		"dispose": function(){
			var view = this;
			this.$el.animate({
				"opacity": 0
			}, 400, function(){
				BaseView.prototype.dispose.apply(view, []);
			});
		},
		"render": function(){
			BaseView.prototype.render.apply(this, []);
			fastdom.write(function(){
				this.$el.css("background-color", this.model.get("_color"));
			}, this);
		}
	});
});