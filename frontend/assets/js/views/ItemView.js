define("views/ItemView", ["views/BaseView"], function(BaseView) {
    "use strict";
    return BaseView.extend({
		"tagName": "option",
        "initialize": function(opt) {
            opt = opt || {};
            this.labelName = opt.labelName;
        },
        "render": function() {
            this.$el.attr("value", this.model.id);
            this.$el.html(this.model.get(this.labelName));
        }
    });
});