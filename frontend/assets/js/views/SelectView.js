define("views/SelectView", ["chaplin", "underscore", "views/ItemView"], function(Chaplin, _, ItemView) {
    "use strict";
    return Chaplin.CollectionView.extend({
		"tagName": "select",
        "itemView": ItemView,
        "listen": {
            "synced collection": "render"
        },
        "events": {
            "change": "changeStatus"
        },
        "initialize": function(opt) {
            opt = opt || {};
            this.status = opt.status;
            this.statusKey = opt.statusKey;
            this.labelName = opt.labelName;
            this.listenTo(this.status, "change:"+this.statusKey, this.render);
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
					"labelName": this.labelName
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
        "render": function() {
            Chaplin.CollectionView.prototype.render.apply(this, _.toArray(arguments));
            var val = this.status.get(this.statusKey);
            if (!val || !this.collection.get(val)) {
                return;
            }
            this.$el.val(val);
        }
    });

});