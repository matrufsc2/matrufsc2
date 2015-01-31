define("views/HistoricItemView", [
    "views/BaseView",
    "backbone",
    "templates"
], function(BaseView, Backbone, templates) {
    "use strict";
	return BaseView.extend({
        "template": templates.historicItem,
        "tagName": "li",
        "events": {
            "click a": "click"
        },
        "initialize": function(options){
            this.plan = options.plan;
        },
        "click": function(){
            this.plan.set({
                "_version": this.model.id
            });
        },
		"getTemplateData": function(){
			return {
				"model": this.model
			};
		}
    });
})