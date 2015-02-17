define("views/PossibilityView", [
    "views/BaseView",
    "backbone",
    "templates"
], function(BaseView, Backbone, templates) {
    "use strict";
	return BaseView.extend({
        "template": templates.possibility,
        "tagName": "li",
        "events": {
            "click a": "click"
        },
        "initialize": function(options){
            this.status = options.status;
        },
        "click": function(e){
            if (this.status.get("editing")){
                return alert("Você não pode mudar de plano enquanto estiver modo de edição");
            }
            this.status.set({
                "possibility": this.model.id
            });
            e.preventDefault();
        },
		"getTemplateData": function(){
			return {
				"model": this.model
			};
		}
    });
});