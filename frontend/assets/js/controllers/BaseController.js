define("controllers/BaseController", ["chaplin", "views/SiteView", "views/HeaderView", "views/FooterView"], function(Chaplin, SiteView, HeaderView, FooterView) {
  "use strict";
  return Chaplin.Controller.extend({
    beforeAction: function() {
      this.reuse("site", SiteView);
      this.reuse("header", HeaderView);
      this.reuse("footer", FooterView);
    }
  });
});