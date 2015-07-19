define("views/RelatedPostsView", ["views/BaseView", "templates"], function (BaseView, templates) {
    "use strict";
    return BaseView.extend({
        "template": templates.relatedPosts,
        "listen": {
            "sync collection": "render"
        },
        "initialize": function (options) {
            this.title = options.title;
        },
        "getTemplateData": function () {
            return {
                "posts": this.collection,
                "title": this.title
            };
        }
    });
});