define("tests/collections/Campi", ["expect", "sinon", "collections/Campi", "models/Campus"], function(expect, sinon, Campi, Campus) {
	"use strict";
	describe("Campi", function(){
		var collection, collectionData = [{
			"id": 3
		}, {
			"id": 5
		}];
		beforeEach(function(){
			collection = new Campi();
			collection.add(collectionData);
		});
		it("Should have Campus as a model", function(){
			expect(collection.model).to.be(Campus);
		});
		it("Should have the same length as the original data", function(){
			expect(collection).to.have.length(collectionData.length);
		});
		it("Should have converted the JSON to models", function(){
			collection.forEach(function(model) {
				expect(model).to.be.a(Campus);
			});
		});
		it("Should have applied default names to all models", function(){
			collection.forEach(function(model) {
				expect(model.get("name")).to.be("Sem nome");
			});
		});
	});
});