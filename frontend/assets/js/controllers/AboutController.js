define("controllers/AboutController", [
	"controllers/BaseController",
	"views/AboutView"
], function(BaseController, AboutView) {
	"use strict";
	return BaseController.extend({
		"index": function(){
			this.adjustTitle("Sobre");
			this.view = new AboutView();
		}
	});
});
