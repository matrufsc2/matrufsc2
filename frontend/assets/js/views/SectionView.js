define("views/SectionView", [
	"templates",
    "underscore",
	"views/BaseView",
    "views/PaginationView",
    "views/SearchFormView",
    "views/CategoriesView"
], function(templates, _, BaseView, PaginationView, SearchFormView, CategoriesView){
	"use strict";
	return BaseView.extend({
		"template" : templates.section,
		"region"   : "main",
        "listen"   : {
            "sync collection": "render"
        },
        "firstTime": true,
        "initialize": function(options) {
            this.sectionsCollection = options.sectionsCollection;
        },
        "getTemplateData": function() {
            return {
                "articles": this.collection,
                "section": this.model,
                "firstTime": this.firstTime
            };
        },
        "render": function() {
            BaseView.prototype.render.apply(this, _.toArray(arguments));
            this.subview("pagination", new PaginationView({
                "container": this.$("#pagination-container"),
                "collection": this.collection,
                "autoRender": true
            }));
            this.subview("searchForm", new SearchFormView({
                "container": this.$(".search-form"),
                "collection": this.collection,
                "autoRender": true
            }));
            if (this.sectionsCollection.get(this.model.id)) {
                this.sectionsCollection.remove(this.model.id);
            }
            this.subview("sections", new CategoriesView({
                "container": this.$(".sections"),
                "autoRender": true,
                "collection": this.sectionsCollection,
                "title": "Outras Seções"
            }));
            this.firstTime = false;
        }
	});
});