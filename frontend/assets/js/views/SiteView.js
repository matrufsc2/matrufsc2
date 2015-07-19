define("views/SiteView", ["templates", "views/BaseView"], function (templates, BaseView) {
    "use strict";
    return BaseView.extend({
        "container": "body",
        "id": "container",
        "regions": {
            "header": "#header",
            "main": "#main",
            "footer": "#footer"
        },
        "template": templates.site
    });
});