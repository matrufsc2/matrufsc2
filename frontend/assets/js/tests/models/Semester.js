define("tests/models/Semester", ["expect", "underscore", "models/Semester"], function(expect, _, Semester) {
	"use strict";
	describe("Semester", function(){
		var model, modelData = {
			"id": 2,
			"name": "2014-1"
		};
		beforeEach(function(){
			model = new Semester(modelData);
		});
		it("Should validate the models correctly", function(){
			model.set({"id": 1, "name": "2014-2"});
			expect(model.validate()).to.be(undefined);
			model.set({"name": "2014"});
			expect(model.validate()).to.not.be(undefined);
		});
	});
});