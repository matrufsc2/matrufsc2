define("views/HistoricListView", [
    "views/BaseView",
    "chaplin",
    "underscore",
    "views/HistoricItemView"
], function (BaseView, Chaplin, _, HistoricItemView) {
    "use strict";
    var HistoricListView = BaseView.extend({
        "itemView": HistoricItemView,
        "tagName": "ul",
        "attributes": {
            "class": "dropdown"
        },
        "initialize": function (options) {
            BaseView.prototype.initialize.call(this, options);
            Chaplin.CollectionView.prototype.initialize.call(this, options);
            this.status = options.status;
            this.listenTo(this.status, "change:version", this.highlightSelectedOption);
            this.listenTo(this.collection, "add", this.highlightSelectedOption); // To track additions...
        },
        "initItemView": function (model) {
            if (this.itemView) {
                return new this.itemView({
                    "model": model,
                    "status": this.status
                });
            } else {
                throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
            }
        },
        "highlightSelectedOption": function () {
            this.$("li.active").removeClass("active");
            var version = this.status.get("version");
            if (!!version) {
                this.$("a[data-id='" + version + "']").parents("li").not(".has-dropdown").addClass("active");
            } else {
                this.$("a").first().parents("li").not(".has-dropdown").addClass("active");
            }
        },
        "render": function () {
            BaseView.prototype.render.call(this);
            Chaplin.CollectionView.prototype.render.call(this);
            this.highlightSelectedOption();
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
});