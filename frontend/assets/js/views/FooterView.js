define("views/FooterView", ["templates", "views/BaseView"], function(templates, BaseView){
	"use strict";
	return BaseView.extend({
		"template": templates.footer,
		"region": "footer"
	});
});