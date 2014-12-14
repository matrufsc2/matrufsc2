define("views/HeaderView", [
	"templates",
	"views/BaseView",
	"jquery",
	"underscore"
], function(templates, BaseView, $, _){
	"use strict";
	return BaseView.extend({
		"template" : templates.header,
		"region"   : "header",
		"listen"   : {
			"router:match mediator": "activateMenuItem",
			"addedToDOM": "applyFoundation"
		},
		"events": {
			"click .start-tour": "startTour",
			"click .share": "share"
		},
		"initialize": function(route) {
			this.activateMenuItem(route);
		},
		"startTour": function(e){
			e.preventDefault();
			if (this.isHome() === false) {
				this.$("#go-to-home").foundation("reveal", "open");
			} else {
				$(document).foundation("joyride", "start", {
					"tip_location_patterns": {
						"top": [],
						"bottom": [],
						"left": ["right", "top", "bottom"],
						"right": ["left", "top", "bottom"]
					}
				});
			}
		},
		"share": function(e) {
			e.preventDefault();
			if (this.isHome() === false) {
				return this.$("#go-to-home").foundation("reveal", "open");
			} else {
				this.$(".share-url").val(window.location.href);
				this.$("#share").foundation("reveal", "open");
				$(".share-url").off("click.select").on("click.select", _.bind(this.selectURL, this));
			}
		},
		"selectURL": function(e) {
			$(e.currentTarget).focus().select();
		},
		"isHome": function(){
			return $(this.$("a[href='/']")).parents("li").is(".active");
		},
		"activateMenuItem": function(route) {
			this.route = route;
			this.render();
		},
		"render": function(){
			BaseView.prototype.render.call(this);
			this.applyFoundation();
			this.$("li.active").removeClass("active");
			this.$("a[href='/"+this.route.path+"']").parents("li").addClass("active");
		}
	});
});