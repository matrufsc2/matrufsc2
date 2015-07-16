define("views/QuestionsGroupView", [
	"templates",
	"underscore",
    "views/BaseView",
    "foundation-accordion"
], function(templates, _, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.questionsGroup,
		"region"   : "main",
        "listen"   : {
            "sync model": "render",
            "render": "applyFoundation"
        },
        "getTemplateData": function() {
            return {
                "model": this.model
            };
        }
	});
});