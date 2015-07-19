define("views/PageView", [
    "templates",
    "underscore",
    "views/BaseView"
], function (templates, _, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.page,
        "region": "main",
        "listen": {
            "sync model": "render"
        },
        "getTemplateData": function () {
            return {
                "model": this.model
            };
        }
    });
});