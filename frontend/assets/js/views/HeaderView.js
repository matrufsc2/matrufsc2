define("views/HeaderView", [
	"templates",
	"views/BaseView",
	"jquery",
	"underscore",
	"views/HistoricListView",
    "views/PossibilitiesView"
], function(templates, BaseView, $, _, HistoricListView, PossibilitiesView){
	"use strict";
	return BaseView.extend({
		"template" : templates.header,
		"region"   : "header",
		"listen"   : {
			"router:match mediator": "activateMenuItem",
			"addedToDOM": "applyFoundation"
		},
		"events": {
			"click .start-tour": "startTour",
			"click .share": "share"
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
		"startTour": function(e){
			e.preventDefault();
			if (this.isHome() === false) {
				this.$("#go-to-home").foundation("reveal", "open");
			} else {
				$(document).foundation("joyride", "start", {
					"tip_location_patterns": {
						"top": [],
						"bottom": [],
						"left": ["right", "top", "bottom"],
						"right": ["left", "top", "bottom"]
					}
				});
			}
		},
		"share": function(e) {
			e.preventDefault();
			if (this.isHome() === false) {
				return this.$("#go-to-home").foundation("reveal", "open");
			} else {
				this.$(".share-url").val("Carregando....");
				var querystring = window.location.href.split("?", 2)[1];
				$.ajax({
					"url": "/api/short/",
					"type": "POST",
					"data": querystring,
					"dataType": "json",
					"success": function(data) {
						$(".share-url").val(data.shortUrl);
					},
					"error": function() {
						$(".share-url").val(window.location.href);
					}
				});
				this.$("#share").foundation("reveal", "open");
				$(".share-url").off("click.select").on("click.select", _.bind(this.selectURL, this));
			}
		},
		"selectURL": function(e) {
			$(e.currentTarget).focus().select();
		},
		"isHome": function(){
			return $(this.$("a[href='/']")).parents("li").is(".active");
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
