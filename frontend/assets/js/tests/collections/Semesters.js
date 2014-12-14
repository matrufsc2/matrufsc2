define("tests/collections/Semesters", ["expect", "sinon", "collections/Semesters", "models/Semester"], function(expect, sinon, Semesters, Semester) {
	"use strict";
	describe("Semesters", function(){
		var collection, collectionData = [{
			"id": 3
		}, {
			"id": 5
		}];
		beforeEach(function(){
			collection = new Semesters();
			collection.add(collectionData);
		});
		it("Should have Semester as a model", function(){
			expect(collection.model).to.be(Semester);
		});
		it("Should have the same length as the original data", function(){
			expect(collection).to.have.length(collectionData.length);
		});
		it("Should have converted the JSON to models", function(){
			collection.forEach(function(model) {
				expect(model).to.be.a(Semester);
			});
		});
	});
});