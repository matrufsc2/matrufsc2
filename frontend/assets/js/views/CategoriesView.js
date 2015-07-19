define("views/CategoriesView", ["views/BaseView", "templates"], function (BaseView, templates) {
    "use strict";
    return BaseView.extend({
        "template": templates.categories,
        "listen": {
            "sync collection": "render"
        },
        "initialize": function (options) {
            this.title = options.title;
        },
        "getTemplateData": function () {
            return {
                "categories": this.collection,
                "title": this.title
            };
        }
    });
});