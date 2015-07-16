define("views/PostView", [
	"templates",
	"underscore",
    "views/BaseView",
    "views/RelatedPostsView",
    "foundation-accordion"
], function(templates, _, BaseView, RelatedPostsView){
	"use strict";
	return BaseView.extend({
		"template" : templates.post,
		"region"   : "main",
        "listen"   : {
            "sync model": "render"
        },
        "getTemplateData": function() {
            return {
                "post": this.model
            };
        },
        "render": function() {
            BaseView.prototype.render.apply(this, _.toArray(arguments));
            this.subview("relatedPosts", new RelatedPostsView({
                "collection": this.collection,
                "title": "Posts relacionados:",
                "container": this.$(".related-posts"),
                "autoRender": true
            }));
        }
	});
});