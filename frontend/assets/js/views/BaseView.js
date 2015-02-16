define("views/BaseView", ["underscore", "chaplin", "foundation"], function (_, Chaplin) {
    "use strict";
    return Chaplin.View.extend({
        "autoRender": true,
        "listen": {
            "addedToDOM": "applyFoundation"
        },
        "getTemplateFunction": function () {
            var template = this.template;
            if (!_.isFunction(template)) {
                template = function () {
                    return "";
                };
            }
            return template;
        },
        "render": function () {
            Chaplin.View.prototype.render.call(this);
            this.attach();
            this.trigger("render");
        },
        "applyFoundation": function () {
            this.$el.foundation();
        }
    });
});