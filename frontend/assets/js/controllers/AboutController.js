define("controllers/AboutController", ["controllers/BaseController", "views/HomeView"], function(BaseController, HomeView) {
	"use strict";
	return BaseController.extend({
		"index": function(){
			this.adjustTitle("Sobre");
			this.view = new HomeView();
		}
	});
});
