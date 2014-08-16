define("views/HeaderView", ["templates", "views/BaseView", "jquery", "fastdom", "foundation"], function(templates, BaseView, $, fastdom){
	"use strict";
	return BaseView.extend({
		"template" : templates.header,
		"region"   : "header",
		"listen"   : {
			"dispatcher:dispatch mediator": "activateMenuItem",
			"addedToDOM": "applyFoundation"
		},
		"events": {
			"click .start-tour": "startTour"
		},
		"startTour": function(){
			fastdom.write(function(){
				$(document).foundation("joyride", "start");
			});	
		},
		"activateMenuItem": function(controller, params, route, options) {
			this.$("li.active").removeClass("active");
			this.$("a[href='/"+route.path.split("'")[0]+"']").parents("li").addClass("active");
		}
	});
});