define("tests/models/Discipline", ["expect", "sinon", "models/Discipline", "collections/Teams"], function(expect, sinon, Discipline, Teams) {
	"use strict";
	describe("Discipline", function(){
		var model, server;
		beforeEach(function(){
			model = new Discipline({
				"id": 2,
				"name": "Calculo A"
			});
			server.respondWith("/api/teams/2.json", [
				200,
				{"Content-Type":"application/json"},
				JSON.stringify([{"id": 4}, {"id": 9}])
			]);
		});
		before(function(){
			server = sinon.fakeServer.create();
		});
		after(function(){
			server.restore();
		});
		it("Should have Teams as an attribute of the object", function(){
			expect(model.teams).to.be.a(Teams);
		});
		it("Should teams have length 2 after fetch", function(done){
			expect(model.teams).to.have.length(0);
			model.teams.fetch().then(function(){
				expect(model.teams).to.have.length(2);
				done();
			}, function(err){
				done(err.thrown);
			});
			server.respond();
		});
		it("Should put default valid values when not present", function(){
			model = new Discipline();
			model.set({"id": 2});
			expect(model.get("_selected")).to.be(false);
			expect(model.get("name")).to.be("Sem nome");
			expect(model.validate()).to.be(undefined);
		});
		it("Should validate the models correctly", function(){
			expect(model.validate()).to.be(undefined);
			model.unset("name");
			expect(model.validate()).to.not.be(undefined);
		});
		describe(".select()", function(){
			it("Should define '_selected' attribute in Discipline as 'true' when called", function(){
				expect(model.get("_selected")).to.be(false);
				model.select();
				expect(model.get("_selected")).to.be(true);
			});
			it("Should define '_selected' attribute in all the teams of the discipline as 'true' when called", function(){
				model.teams.forEach(function(team){
					expect(team.get("_selected")).to.be(false);
				});
				model.select();
				model.teams.forEach(function(team){
					expect(team.get("_selected")).to.be(true);
				});
			});
		});
		describe(".unselect()", function(){
			beforeEach(function(){
				model.select();
			});
			it("Should define '_selected' attribute in Discipline as 'false' when called", function(){
				expect(model.get("_selected")).to.be(true);
				model.unselect();
				expect(model.get("_selected")).to.be(false);
			});
			it("Should define '_selected' attribute in all the teams of the discipline as 'false' when called", function(){
				model.teams.forEach(function(team){
					expect(team.get("_selected")).to.be(true);
				});
				model.unselect();
				model.teams.forEach(function(team){
					expect(team.get("_selected")).to.be(false);
				});
			});
		});
		describe(".moveUp()", function(){
			it("Should be a function", function(){
				expect(model.moveUp).to.be.a("function");
			});
			it("Should call moveUp on collection with the correct model", function(){
				model.collection = {};
				model.collection.moveUp = sinon.spy();
				model.moveUp();
				expect(model.collection.moveUp.calledOnce).to.be(true);
				expect(model.collection.moveUp.calledWith(model)).to.be(true);
			});
			it("Should throw an exception if collection is undefined", function() {
				expect(function(){
					model.moveUp();
				}).to.throwError(/Cannot move up without a collection defined/);
			});
		});
		describe(".moveDown()", function(){
			it("Should be a function", function(){
				expect(model.moveDown).to.be.a("function");
			});
			it("Should call moveDown on collection with the correct model", function(){
				model.collection = {};
				model.collection.moveDown = sinon.spy();
				model.moveDown();
				expect(model.collection.moveDown.calledOnce).to.be(true);
				expect(model.collection.moveDown.calledWith(model)).to.be(true);
			});
			it("Should throw an exception if collection is undefined", function() {
				expect(function(){
					model.moveDown();
				}).to.throwError(/Cannot move down without a collection defined/);
			});
		});
		describe(".position()", function(){
			it("Should be a function", function(){
				expect(model.position).to.be.a("function");
			});
			it("Should call indexOf on collection with the correct model", function(){
				var position = Math.floor(Math.random()*1000);
				model.collection = {};
				model.collection.indexOf = sinon.stub().returns(position);
				var result = model.position();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
				expect(result).to.be(position);
			});
			it("Should throw an exception if collection is undefined", function(){
				expect(function(){
					model.position();
				}).to.throwError(/Cannot get a position in the collection without a collection defined/);
			});
		});
		describe(".isFirst()", function(){
			it("Should be a function", function(){
				expect(model.isFirst).to.be.a("function");
			});
			it("Should call indexOf on collection with the correct model", function(){
				model.collection = {};
				model.collection.indexOf = sinon.spy();
				model.isFirst();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
			});
			it("Should return true if the model is at 0 index", function(){
				model.collection = {};
				model.collection.indexOf = sinon.stub().returns(0);
				var result = model.isFirst();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
				expect(result).to.be(true);
			});
			it("Should return false if the model is at index greater than 0", function(){
				var position = Math.floor(Math.random()*1000) + 1;
				model.collection = {};
				model.collection.indexOf = sinon.stub().returns(position);
				var result = model.isFirst();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
				expect(position).to.be.greaterThan(0);
				expect(result).to.be(false);
			});
			it("Should throw an exception if collection is undefined", function(){
				expect(function(){
					model.isFirst();
				}).to.throwError(/Cannot get a position in the collection without a collection defined/);
			});
		});
		describe(".isLast()", function(){
			it("Should be a function", function(){
				expect(model.isLast).to.be.a("function");
			});
			it("Should call indexOf on collection with the correct model", function(){
				model.collection = {};
				model.collection.indexOf = sinon.spy();
				model.collection.length = 2;
				model.isLast();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
			});
			it("Should return true if the model is at last index", function(){
				model.collection = {};
				model.collection.indexOf = sinon.stub().returns(1);
				model.collection.length = 2;
				var result = model.isLast();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
				expect(result).to.be(true);
			});
			it("Should return false if the model is the first in the collection", function(){
				var length = Math.floor(Math.random()*1000) + 2;
				model.collection = {};
				model.collection.indexOf = sinon.stub().returns(0);
				model.collection.length = length;
				var result = model.isLast();
				expect(model.collection.indexOf.calledOnce).to.be(true);
				expect(model.collection.indexOf.calledWith(model)).to.be(true);
				expect(result).to.be(false);
			});
			it("Should throw an exception if collection is undefined", function(){
				expect(function(){
					model.isLast();
				}).to.throwError(/Cannot get a position in the collection without a collection defined/);
			});
		});
	});
});