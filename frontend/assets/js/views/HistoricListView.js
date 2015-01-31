define("views/HistoricListView", [
    "views/BaseView",
    "chaplin",
    "underscore",
    "views/HistoricItemView"
], function(BaseView, Chaplin, _, HistoricItemView) {
    "use strict";
	var HistoricListView = BaseView.extend({
        "itemView": HistoricItemView,
		"tagName": "ul",
		"attributes": {
			"class": "dropdown"
		},
		"initialize": function(options){
			BaseView.prototype.initialize.call(this, options);
			Chaplin.CollectionView.prototype.initialize.call(this, options);
            this.plan = options.plan;
		},
        "initItemView": function(model) {
			if (this.itemView) {
				return new this.itemView({
					model: model,
					plan: this.plan
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
		"render": function(){
			BaseView.prototype.render.call(this);
			Chaplin.CollectionView.prototype.render.call(this);
			this.$("li.active").removeClass("active");
            if (this.plan.has("_version")) {
                this.$("a[data-id='"+this.plan.get("_version")+"']").parents("li").addClass("active");
            }
		}
    });
	_.extend(HistoricListView.prototype,
		_.omit(
			Chaplin.CollectionView.prototype,
			_.keys(HistoricListView.prototype),
			_.keys(BaseView.prototype)
		)
	);
    return HistoricListView;
})