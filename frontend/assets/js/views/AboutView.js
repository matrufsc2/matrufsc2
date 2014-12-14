define("views/AboutView", [
	"templates",
	"underscore",
	"views/BaseView",
], function(templates, _, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.about,
		"region"   : "main"
	});
});