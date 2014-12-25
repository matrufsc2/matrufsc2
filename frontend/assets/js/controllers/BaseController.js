define("controllers/BaseController", [
  "chaplin",
  "underscore",
  "collections/HistoryCollection",
  "views/SiteView",
  "views/HeaderView",
  "views/FooterView"
], function(Chaplin, _, HistoryCollection, SiteView, HeaderView, FooterView) {
  "use strict";
  return Chaplin.Controller.extend({
    "initialize": function(){
      Chaplin.Controller.prototype.initialize.call(this);
      this.historyCollection = null;
      this.header = null;
    },
    "getHistory": function(){
      if (!this.historyCollection || this.historyCollection.disposed) {
        this.historyCollection = new HistoryCollection();
        this.historyCollection.fetch();
        while (this.historyCollection.length >= 10) {
          var model = this.historyCollection.pop();
          model.collection = this.historyCollection;
          model.destroy();
        }
      }
      this.historyCollection.sort();
      return this.historyCollection;
    },
    "getHeader": function(){
      if (!this.header || this.header.disposed) {
        this.header = new HeaderView({
          "route": this.route,
          "historyCollectionGetter": _.bind(this.getHistory, this)
        });
      }
      return this.header;
    },
    "beforeAction": function(params, route) {
      this.route = route;
      this.reuse("site", SiteView);
      this.reuse("header", {
        "compose": _.bind(this.getHeader, this)
      });
      this.reuse("footer", FooterView);
      this.getHeader().render();
    }
  });
});