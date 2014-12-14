define(["config"], function() {
	"use strict";
	return require(["mocha"], function(){
		mocha.setup("bdd");
		function loadTests(){
			return require(["tests/bootstrapper"], function(){
				mocha.checkLeaks();
				mocha.run(function(){
					var xhr = new XMLHttpRequest();
					xhr.open("POST", "http://localhost:7358/", true);
					xhr.send(JSON.stringify(window.__coverage__));
				});
			});
		}
		// Will require test'em, and load tests when test'em is found and
		// when test'em is not found
		return require(["testem"], loadTests, loadTests);
	});
});