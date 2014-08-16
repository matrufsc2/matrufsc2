define("tests/collections/Disciplines", ["expect", "sinon", "collections/Disciplines", "models/Discipline"], function(expect, sinon, Disciplines, Discipline) {
	"use strict";
	describe("Disciplines", function(){
		var collection, collectionData = [{
			"id": 3
		}, {
			"id": 5
		}, {
			"id": 9
		}];
		beforeEach(function(){
			collection = new Disciplines();
			collection.add(collectionData);
		});
		it("Should have Discipline as a model", function(){
			expect(collection.model).to.be(Discipline);
		});
		it("Should have the same length as the original data", function(){
			expect(collection).to.have.length(collectionData.length);
		});
		it("Should have converted the JSON to models", function(){
			collection.forEach(function(model) {
				expect(model).to.be.a(Discipline);
			});
		});
		describe(".moveUp()", function(){
			it("Should be a function", function(){
				expect(collection.moveUp).to.be.a("function");
			});
			it("Should be capable of moving the second model to the first model", function(){
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
				collection.moveUp(collection.at(1));
				expect(collection.at(0).id).to.be(5);
				expect(collection.at(1).id).to.be(3);
				expect(collection.at(2).id).to.be(9);
			});
			it("Should be no-op when moving up the first model", function(){
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
				collection.moveUp(collection.at(0));
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
			});
		});
		describe(".moveDown()", function(){
			it("Should be a function", function(){
				expect(collection.moveDown).to.be.a("function");
			});
			it("Should be capable of moving the second model to the third model", function(){
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
				collection.moveDown(collection.at(1));
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(9);
				expect(collection.at(2).id).to.be(5);
			});
			it("Should be no-op when moving down the last model", function(){
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
				collection.moveDown(collection.at(2));
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
			});
		});
		describe(".moveTo()", function(){
			it("To be a function", function(){
				expect(collection.moveTo).to.be.a("function");
			});
			it("Should be capable of move the first model to the third model", function(){
				expect(collection.at(0).id).to.be(3);
				expect(collection.at(1).id).to.be(5);
				expect(collection.at(2).id).to.be(9);
				collection.moveTo(collection.at(0), 2);
				expect(collection.at(0).id).to.be(5);
				expect(collection.at(1).id).to.be(9);
				expect(collection.at(2).id).to.be(3);
			});
		});
	});
});