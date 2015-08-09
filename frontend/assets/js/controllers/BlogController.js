define("controllers/BlogController", [
    "chaplin",
    "underscore",
    "backbone",
    "controllers/BaseController",
    "collections/Posts",
    "models/Category",
    "views/BlogView",
    "views/CategoryView",
    "collections/Categories"
], function (Chaplin, _, Backbone, BaseController, Posts, Category, BlogView, CategoryView, Categories) {
    "use strict";
    return BaseController.extend({
        "getCategoriesCollection": function () {
            var categoriesCollection = new Categories();
            categoriesCollection.fetch();
            return categoriesCollection;
        },
        "index": function (params, metadata, request) {
            this.adjustTitle("Blog");
            this.collection = new Posts();
            this.collection.currentPage = parseInt(request.query.page, 10) || 1;
            this.collection.query = request.query.q;
            this.listenTo(this.collection, "sync", function () {
                var data = {};
                if (this.collection.currentPage !== 1) {
                    data.page = this.collection.currentPage;
                }
                if (this.collection.getQuery()) {
                    data.q = this.collection.getQuery();
                }
                if (!data.q && !data.page) {
                    return;
                }
                Backbone.history.navigate(
                    Chaplin.utils.reverse("Blog#index", {
                        "id": params.id,
                        "slug": params.slug
                    }, data),
                    {"trigger": true, "replace": false}
                );
            });
            this.view = new BlogView({
                "collection": this.collection,
                "categoriesCollection": this.getCategoriesCollection()
            });
            this.collection.fetch();
        },
        "category": function (params, metadata, request) {
            this.adjustTitle("Blog");
            this.collection = new Posts();
            this.model = new Category({
                "id": params.id
            });
            this.view = new CategoryView({
                "collection": this.collection,
                "model": this.model,
                "categoriesCollection": this.getCategoriesCollection()
            });
            this.listenTo(this.model, "sync", function () {
                this.adjustTitle(this.model.get("title") + " - Blog");
                this.collection.currentPage = parseInt(request.query.page, 10) || 1;
                this.collection.q = request.query.q;
                this.collection.url = "/api/posts/?category=" + this.model.id;
                this.listenTo(this.collection, "sync", function () {
                    var data = {};
                    if (this.collection.currentPage !== 1) {
                        data.page = this.collection.currentPage;
                    }
                    if (this.collection.getQuery()) {
                        data.q = this.collection.getQuery();
                    }
                    if (!data.q && !data.page) {
                        return;
                    }
                    Backbone.history.navigate(
                        Chaplin.utils.reverse("Blog#category", {
                            "id": params.id,
                            "slug": params.slug
                        }, data),
                        {"trigger": true, "replace": false}
                    );
                });
                if (params.slug !== this.model.get("slug")) {
                    var url = Chaplin.utils.reverse("Blog#category", {
                        "id": this.model.id,
                        "slug": this.model.get("slug")
                    });
                    Backbone.history.navigate(url, {"trigger": true, "replace": true});
                    return;
                }
                this.collection.fetch();
            });
            this.model.fetch();
        }
    });
});
