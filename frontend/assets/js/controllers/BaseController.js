define("controllers/BaseController", [
    "chaplin",
    "underscore",
    "jquery",
    "models/User",
    "views/SiteView",
    "views/HeaderView",
    "views/FooterView"
], function (Chaplin, _, $, User, SiteView, HeaderView, FooterView) {
    "use strict";
    return Chaplin.Controller.extend({
        "initialize": function () {
            Chaplin.Controller.prototype.initialize.call(this);
            this.header = null;
            this.user = new User({
                "id": "current"
            });
            this.user.fetch();
        },
        "getHeader": function () {
            if (!this.header || this.header.disposed) {
                this.header = new HeaderView({
                    "route": this.route,
                    "user": this.user
                });
            }
            return this.header;
        },
        "beforeAction": function (params, route) {
            this.route = route;
            this.reuse("site", SiteView);
            this.reuse("header", {
                "compose": _.bind(function () {
                    return this.getHeader();
                }, this),
                "check": function () {
                    return false;
                }
            });
            this.reuse("footer", FooterView);
            if (!!window.ga) {
                // Alert Google Analytics that the route changed
                ga('send', 'pageview', "/"+route.path+"?"+route.query);
            }
        }
    });
});