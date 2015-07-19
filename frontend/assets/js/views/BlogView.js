define("views/BlogView", [
    "templates",
    "underscore",
    "views/BaseView",
    "views/PaginationView",
    "views/SearchFormView",
    "views/CategoriesView"
], function (templates, _, BaseView, PaginationView, SearchFormView, CategoriesView) {
    "use strict";
    return BaseView.extend({
        "template": templates.blog,
        "region": "main",
        "listen": {
            "sync collection": "render"
        },
        "firstTime": true,
        "initialize": function (options) {
            this.categoriesCollection = options.categoriesCollection;
        },
        "getTemplateData": function () {
            return {
                "posts": this.collection,
                "firstTime": this.firstTime
            };
        },
        "render": function () {
            BaseView.prototype.render.apply(this, _.toArray(arguments));
            this.subview("pagination", new PaginationView({
                "container": this.$("#pagination-container"),
                "collection": this.collection,
                "autoRender": true
            }));
            this.subview("searchForm", new SearchFormView({
                "container": this.$(".search-form"),
                "collection": this.collection,
                "autoRender": true,
                "titleElement": this.$()
            }));
            this.subview("categories", new CategoriesView({
                "container": this.$(".categories"),
                "autoRender": true,
                "collection": this.categoriesCollection,
                "title": "Categorias"
            }));
            this.firstTime = false;
        }
    });
});