define("views/QuestionsGroupsView", [
	"templates",
	"underscore",
    "please",
	"views/BaseView",
    "foundation-equalizer"
], function(templates, _, Please, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.questionsGroups,
		"region"   : "main",
        "listen"   : {
            "sync collection": "render",
            "render": "applyFoundation"
        },
        "firstTime": true,
        "getTemplateData": function() {
            return {
                "questionsGroups": this.collection,
                "getRandomColor": this.getRandomColor,
                "firstTime": this.firstTime
            };
        },
        "render": function() {
            BaseView.prototype.render.apply(this, _.toArray(arguments));
            this.firstTime = false;
        },
        "getRandomColor": function() {
            return Please.make_color({
                "saturation": 0.3,
                "value": (Math.floor(Math.random()*25)+75)/100
            })[0];
        }
	});
});