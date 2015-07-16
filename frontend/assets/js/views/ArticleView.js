define("views/ArticleView", [
	"templates",
	"underscore",
    "views/BaseView",
    "foundation-accordion"
], function(templates, _, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.article,
		"region"   : "main",
        "listen"   : {
            "sync model": "render"
        },
        "getTemplateData": function() {
            return {
                "article": this.model
            };
        }
	});
});