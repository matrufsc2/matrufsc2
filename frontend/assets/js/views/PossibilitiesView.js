define("views/PossibilitiesView", [
    "views/BaseView",
    "chaplin",
    "underscore",
    "views/PossibilityView"
], function(BaseView, Chaplin, _, PossibilityView) {
    "use strict";
	var PossibilitiesView = BaseView.extend({
        "itemView": PossibilityView,
		"tagName": "ul",
		"attributes": {
			"class": "dropdown"
		},
		"initialize": function(options){
			BaseView.prototype.initialize.call(this, options);
			Chaplin.CollectionView.prototype.initialize.call(this, options);
            this.status = options.status;
            this.listenTo(this.status, "change:possibility", this.highlightSelectedOption);
		},
        "initItemView": function(model) {
			if (this.itemView) {
				return new this.itemView({
					"model": model,
					"status": this.status
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
        "highlightSelectedOption": function(){
            this.$("li.active").removeClass("active");
            var possibility = this.status.get("possibility");
            this.$("a[data-id='"+possibility+"']").parents("li").not(".has-dropdown").addClass("active");
        },
		"render": function(){
			BaseView.prototype.render.call(this);
			Chaplin.CollectionView.prototype.render.call(this);
            this.highlightSelectedOption();
		}
    });
	_.extend(PossibilitiesView.prototype,
		_.omit(
			Chaplin.CollectionView.prototype,
			_.keys(PossibilitiesView.prototype),
			_.keys(BaseView.prototype)
		)
	);
    return PossibilitiesView;
});