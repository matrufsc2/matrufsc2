define("views/HeaderView", [
	"templates",
	"views/BaseView",
	"jquery",
	"underscore",
	"views/HistoricListView",
    "views/PossibilitiesView",
    "foundation-topbar",
    "foundation-dropdown"
], function(templates, BaseView, $, _, HistoricListView, PossibilitiesView){
	"use strict";
	return BaseView.extend({
		"template" : templates.header,
		"region"   : "header",
		"listen"   : {
			"router:match mediator": "activateMenuItem",
			"addedToDOM": "applyFoundation"
		},
		"initialize": function(options) {
            BaseView.prototype.initialize.call(this, options);
            this.history = options.history;
            this.possibilities = options.possibilities;
            this.status = options.status;
            this.user = options.user;
            this.listenTo(this.user, "change", this.updateAuthInfo);
            this.activateMenuItem(options.route);
        },
		"isHome": function(){
			return this.$("a[href='/']").parents("li").is(".active");
		},
		"activateMenuItem": function(route) {
			this.route = route;
			this.render();
		},
        "updateAuthInfo": function(){
            var auth = this.$(".auth");
            if (this.user.get("is_authenticated")) {
                auth.attr("href", this.user.get("logout_url")).html("Sair");
            } else {
                auth.attr("href", this.user.get("login_url")).html("Entrar");
            }
        },
        "updateHistory": function(){
            var history = this.$(".history");
            history.off("click");
            if (this.history) {
                this.subview("history", new HistoricListView({
                    "collection": this.history,
                    "status": this.status,
                    "container": history
                }));
                history.removeClass("active");
            } else {
                history.on("click", _.bind(function(){
                    this.$("#go-to-home").foundation("reveal", "open");
                }, this));
            }
        },
        "updatePossibilities": function(){
            var possibilities = this.$(".possibilities");
            possibilities.off("click");
            if (this.history) {
                this.subview("possibilities", new PossibilitiesView({
                    "collection": this.possibilities,
                    "status": this.status,
                    "container": possibilities
                }));
                possibilities.removeClass("active");
            } else {
                possibilities.on("click", _.bind(function(){
                    this.$("#go-to-home").foundation("reveal", "open");
                }, this));
            }
        },
        "updateActiveItem": function(){
            this.$("li.active").removeClass("active");
			this.$("a[href='/"+this.route.path+"']").parents("li").not(".has-dropdown").addClass("active");
        },
		"render": function(){
			BaseView.prototype.render.call(this);
			this.applyFoundation();
			this.updateActiveItem();
            this.updateHistory();
            this.updatePossibilities();
            this.updateAuthInfo();
		}
	});
});
