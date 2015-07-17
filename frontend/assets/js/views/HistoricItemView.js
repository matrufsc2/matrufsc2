define("views/HistoricItemView", [
    "views/BaseView",
    "underscore",
    "backbone",
    "templates"
], function(BaseView, _, Backbone, templates) {
    "use strict";
	return BaseView.extend({
        "template": templates.historicItem,
        "tagName": "li",
        "events": {
            "click a": "click"
        },
        "initialize": function(options){
            this.status = options.status;
        },
        "click": function(e){
            if (this.status.get("editing")){
                return alert("Você não pode consultar itens no histórico enquanto estiver modo de edição");
            }
            this.status.set({
                "version": this.model.id
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