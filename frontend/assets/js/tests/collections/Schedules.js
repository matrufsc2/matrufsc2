define("tests/collections/Schedules", ["expect", "sinon", "collections/Schedules", "models/Schedule"], function(expect, sinon, Schedules, Schedule) {
	"use strict";
	describe("Schedules", function(){
		var collection, collectionData = [{
			"id": 3
		}, {
			"id": 5
		}];
		beforeEach(function(){
			collection = new Schedules();
			collection.add(collectionData);
		});
		it("Should have Schedule as a model", function(){
			expect(collection.model).to.be(Schedule);
		});
		it("Should have the same length as the original data", function(){
			expect(collection).to.have.length(collectionData.length);
		});
		it("Should have converted the JSON to models", function(){
			collection.forEach(function(model) {
				expect(model).to.be.a(Schedule);
			});
		});
		it("Should have applied default values to all models", function(){
			collection.forEach(function(model) {
				expect(model.get("hourStart")).to.be(0);
				expect(model.get("minuteStart")).to.be(0);
				expect(model.get("hourEnd")).to.be(0);
				expect(model.get("minuteEnd")).to.be(0);
				expect(model.get("dayOfWeek")).to.be(2);
				expect(model.get("room")).to.be("AUX/ALOCAR");
			});
		});
	});
});