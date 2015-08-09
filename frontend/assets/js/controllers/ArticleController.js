define("controllers/ArticleController", [
    "underscore",
    "backbone",
    "chaplin",
    "controllers/BaseController",
    "models/Article",
    "views/ArticleView"
], function (_, Backbone, Chaplin, BaseController, Article, ArticleView) {
    "use strict";
    return BaseController.extend({
        "index": function (params) {
            this.model = new Article({
                "id": params.id
            });
            this.view = new ArticleView({
                "model": this.model
            });
            this.listenTo(this.model, "sync", function () {
                if (!this.model.has("title") && !this.model.has("body")) {
                    alert("Este artigo não existe! Redirecionando para a página principal..");
                    Backbone.history.navigate("/", {"replace": true, "trigger": true});
                } else {
                    if (params.slug !== this.model.get("slug")) {
                        var url = Chaplin.utils.reverse("Article#index", {
                            "id": this.model.id,
                            "slug": this.model.get("slug")
                        });
                        Backbone.history.navigate(url, {
                            "replace": true,
                            "trigger": true
                        });
                        return;
                    }
                    this.adjustTitle(this.model.get("title") + " - Artigos - Ajuda");
                }
            });
            this.model.fetch();
        }
    });
});
