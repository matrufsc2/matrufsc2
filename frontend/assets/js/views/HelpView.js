define("views/HelpView", [
    "templates",
    "underscore",
    "please",
    "views/BaseView",
    "foundation-equalizer"
], function (templates, _, Please, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.help,
        "region": "main",
        "listen": {
            "sync collection": "render",
            "render": "applyFoundation"
        },
        "getTemplateData": function () {
            return {
                "sections": this.collection,
                "getRandomColor": this.getRandomColor
            };
        },
        "getRandomColor": function () {
            return Please.make_color({
                "saturation": 0.2,
                "value": (Math.floor(Math.random() * 25) + 75) / 100
            })[0];
        }
    });
});