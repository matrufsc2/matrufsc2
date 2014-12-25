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
			this.url = options.url;
		},
		"render": function(){
			BaseView.prototype.render.call(this);
			Chaplin.CollectionView.prototype.render.call(this);
			this.$("li.active").removeClass("active");
			this.$("a[href='"+this.url+"']").parents("li").addClass("active");
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