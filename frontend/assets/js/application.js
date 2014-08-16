define("application", ['chaplin'], function(Chaplin) {
	"use strict";
	return Chaplin.Application.extend({
		title: 'MatrUFSC2',
		"initDispatcher": function(){
			this.dispatcher = new Chaplin.Dispatcher({
				"controllerSuffix": "Controller"
			});
		}
	});
});