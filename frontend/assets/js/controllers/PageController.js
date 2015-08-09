define("controllers/PageController", [
    "underscore",
    "backbone",
    "controllers/BaseController",
    "models/Page",
    "views/PageView"
], function (_, Backbone, BaseController, Page, PageView) {
    "use strict";
    return BaseController.extend({
        "index": function (params) {
            this.model = new Page({
                "id": params.id
            });
            this.view = new PageView({
                "model": this.model
            });
            this.listenTo(this.model, "sync", function () {
                if (!this.model.has("title") && !this.model.has("body") && !this.model.has("slug")) {
                    alert("A página não existe! Redirecionando para a página principal..");
                    Backbone.history.navigate("/", {"replace": true, "trigger": true});
                } else {
                    if (params.slug !== this.model.get("slug")) {
                        Backbone.history.navigate("/" + this.model.get("slug") + "/" + this.model.id, {
                            "replace": true,
                            "trigger": true
                        });
                        return;
                    }
                    this.adjustTitle(this.model.get("title"));
                }
            });
            this.model.fetch();
        }
    });
});
