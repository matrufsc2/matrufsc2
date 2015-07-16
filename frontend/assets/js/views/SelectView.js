define("views/SelectView", ["chaplin", "views/ItemView"], function(Chaplin, ItemView) {
    "use strict";
    return Chaplin.CollectionView.extend({
		"tagName": "select",
        "itemView": ItemView,
        "listen": {
            "synced collection": "renderAllItems"
        },
        "events": {
            "change": "changeStatus"
        },
        "initialize": function(opt) {
            opt = opt || {};
            this.status = opt.status;
            this.statusKey = opt.statusKey;
            this.labelName = opt.labelName;
            this.listenTo(this.status, "change:"+this.statusKey, this.renderAllItems);
        },
        "changeStatus": function() {
            var attrs = {};
            attrs[this.statusKey] = this.$el.val();
            if (this.status.get(this.statusKey) === this.$el.val()) {
                return;
            }
            this.status.set(attrs);
        },
        "initItemView": function(model){
			if (this.itemView) {
				return new this.itemView({
					"model": model,
					"labelName": this.labelName,
                    "attributes": {
                        "selected": this.status.get(this.statusKey) === model.id
                    }
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
    });

});