define("views/HistoricItemView", [
    "views/BaseView",
    "backbone",
    "templates"
], function(BaseView, Backbone, templates) {
    "use strict";
	return BaseView.extend({
        "template": templates.historicItem,
        "tagName": "li",
		"getTemplateData": function(){
			return {
				"model": this.model
			};
		}
    });
})