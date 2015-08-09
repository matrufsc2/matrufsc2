define("controllers/PostController", [
    "underscore",
    "backbone",
    "chaplin",
    "controllers/BaseController",
    "models/Post",
    "collections/Posts",
    "views/PostView"
], function (_, Backbone, Chaplin, BaseController, Post, Posts, PostView) {
    "use strict";
    return BaseController.extend({
        "index": function (params) {
            this.model = new Post({
                "id": params.id
            });
            this.collection = new Posts();
            this.collection.url = "/api/posts?similar=" + params.id;
            this.view = new PostView({
                "model": this.model,
                "collection": this.collection
            });
            this.listenTo(this.model, "sync", function () {
                if (!this.model.has("title") && !this.model.has("body")) {
                    alert("Este post não existe! Redirecionando para a página principal..");
                    Backbone.history.navigate("/", {"replace": true, "trigger": true});
                } else {
                    if (params.slug !== this.model.get("slug")) {
                        var url = Chaplin.utils.reverse("Post#index", {
                            "id": this.model.id,
                            "slug": this.model.get("slug")
                        });
                        Backbone.history.navigate(url, {
                            "replace": true,
                            "trigger": true
                        });
                        return;
                    }
                    this.adjustTitle(this.model.get("title") + " - Blog");
                    this.collection.fetch();
                    if (window.FB && this.model.get("allow_comments") === true) {
                        // Parse the Facebook Comments if possible
                        window.FB.XFBML.parse();
                    }
                }
            });
            this.model.fetch();
        }
    });
});
