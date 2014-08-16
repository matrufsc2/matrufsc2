define("tests/models/Campus", ["expect", "underscore", "models/Campus", "collections/Disciplines"], function(expect, _, Campus, Disciplines) {
	"use strict";
	describe("Campus", function(){
		var model, modelData = {
			"id": 2,
			"name": "Calculo A",
			"disciplines": [{
				"id": 4,
				"name": "Calculo A"
			}, {
				"id": 2,
				"name": "Sistemas Digitais"
			}]
		};
		beforeEach(function(){
			model = new Campus(modelData);
		});
		it("Should have Disciplines as an attribute of the object", function(){
			expect(model.disciplines).to.be.a(Disciplines);
			expect(model.disciplines.pluck("id")).to.eql(_.pluck(model.get("disciplines"), "id"));
			expect(model.disciplines.pluck("name")).to.eql(_.pluck(model.get("disciplines"), "name"));
		});
		it("Should teams have length 2", function(){
			expect(model.disciplines).to.have.length(2);
		});
		it("Should put default valid values when not present", function(){
			model = new Campus();
			model.set({"id": 2});
			expect(model.get("name")).to.be("Sem nome");
			expect(model.get("disciplines")).to.be.an("array");
			expect(model.get("disciplines")).to.have.length(0);
			expect(model.validate()).to.be(undefined);
		});
		it("Should validate the models correctly", function(){
			expect(model.validate()).to.be(undefined);
			model.unset("disciplines");
			expect(model.validate()).to.not.be(undefined);
		});
	});
});