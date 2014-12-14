define("tests/models/Teacher", ["expect",  "models/Teacher"], function(expect, Teacher) {
	"use strict";
	describe("Teacher", function(){
		var model;
		beforeEach(function(){
			model = new Teacher({
				"id": 2,
				"name": "Foo"
			});
		});
		it("Should put default valid values when not present", function(){
			model = new Teacher();
			model.set({"id": 2});
			expect(model.get("name")).to.be("Sem nome");
			expect(model.validate()).to.be(undefined);
		});
		it("Should validate the models correctly", function(){
			expect(model.validate()).to.be(undefined);
			model.unset("name");
			expect(model.validate()).to.not.be(undefined);
		});
	});
});