define("controllers/HelpController", [
    "chaplin",
    "underscore",
    "backbone",
    "controllers/BaseController",
    "collections/Articles",
    "models/Section",
    "views/HelpView",
    "views/SectionView",
    "collections/Sections"
], function (Chaplin, _, Backbone, BaseController, Articles, Section, HelpView, SectionView, Sections) {
    "use strict";
    return BaseController.extend({
        "getSectionsCollection": function () {
            var sectionsCollection = new Sections();
            sectionsCollection.fetch();
            return sectionsCollection;
        },
        "index": function (params, metadata, request) {
            this.adjustTitle("Ajuda");
            this.collection = new Sections();
            this.collection.currentPage = parseInt(request.query.page, 10) || 1;
            this.collection.query = request.query.q;
            this.listenTo(this.collection, "sync", function () {
                var data = {};
                if (this.collection.currentPage !== 1) {
                    data.page = this.collection.currentPage;
                } else {
                    return;
                }
                Backbone.history.navigate(
                    Chaplin.utils.reverse("Help#index", {
                        "id": params.id,
                        "slug": params.slug
                    }, data),
                    {"trigger": true, "replace": false}
                );
            });
            this.view = new HelpView({
                "collection": this.collection,
                "sectionsCollection": this.getSectionsCollection()
            });
            this.collection.fetch();
        },
        "section": function (params, metadata, request) {
            this.adjustTitle("Ajuda");
            this.collection = new Articles();
            this.model = new Section({
                "id": params.id
            });
            this.view = new SectionView({
                "collection": this.collection,
                "model": this.model,
                "sectionsCollection": this.getSectionsCollection()
            });
            this.listenTo(this.model, "sync", function() {
                this.adjustTitle(this.model.get("title") + " - Ajuda");
                this.collection.currentPage = parseInt(request.query.page, 10) || 1;
                this.collection.query = request.query.q;
                this.collection.url = "/api/articles/?section=" + this.model.id;
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
                        Chaplin.utils.reverse("Help#section", {
                            "id": params.id,
                            "slug": params.slug
                        }, data),
                        {"trigger": true, "replace": false}
                    );
                });
                if (params.slug !== this.model.get("slug")) {
                    var url = Chaplin.utils.reverse("Help#section", {
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
