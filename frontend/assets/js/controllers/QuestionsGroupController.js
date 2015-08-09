define("controllers/QuestionsGroupController", [
    "underscore",
    "backbone",
    "controllers/BaseController",
    "models/QuestionsGroup",
    "views/QuestionsGroupView"
], function (_, Backbone, BaseController, QuestionsGroup, QuestionsGroupView) {
    "use strict";
    return BaseController.extend({
        "index": function (params) {
            this.model = new QuestionsGroup({
                "id": params.id
            });
            this.view = new QuestionsGroupView({
                "model": this.model
            });
            this.listenTo(this.model, "sync", function () {
                if (!this.model.has("title") && !this.model.has("body")) {
                    alert("A página não existe! Redirecionando para a página principal..");
                    Backbone.history.navigate("/", {"replace": true, "trigger": true});
                } else {
                    if (params.slug !== this.model.get("slug")) {
                        Backbone.history.navigate("/perguntas-frequentes/" + this.model.get("slug") + "/" + this.model.id, {
                            "replace": true,
                            "trigger": true
                        });
                        return;
                    }
                    this.adjustTitle(this.model.get("title") + " - Perguntas Frequentes");
                }
            });
            this.model.fetch();
        }
    });
});
