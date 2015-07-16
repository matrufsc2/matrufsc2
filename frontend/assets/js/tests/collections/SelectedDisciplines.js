define("tests/collections/SelectedDisciplines", ["expect", "sinon", "collections/SelectedDisciplines"], function(expect, sinon, SelectedDisciplines) {
	"use strict";
	describe("SelectedDisciplines", function(){
		var parentCollection, collection, collectionData = [{
			"id" : 1,
			"code": "A1",
			"_selected" : false,
			
		},{
			"id": 3,
			"code": "A2",
			"_selected" : true
		}, {
			"id": 5,
			"code": "A3",
			"_selected": true
		}, {
			"id": 9,
			"code": "A4",
			"_selected" : true
		}];
		var server;
		beforeEach(function(){
			collection = new SelectedDisciplines([]);
			parentCollection.add(collectionData);
		});
		before(function(){
			server = sinon.fakeServer.create();
			for(var count = 0; count < collectionData.length; count ++ ) {
				server.respondWith("/api/teams/"+collectionData[count].id+".json", [
					200,
					{
						"Content-Type": "application/json"
					},
					JSON.stringify([
						{
							"id": (count*10)-1,
							"schedules": [{
								"id": collectionData[count].id,
								"hourStart": collectionData[count].id+1,
								"minuteStart": 0,
								"hourEnd": collectionData[count].id+2,
								"minuteEnd": 30,
								"dayOfWeek": 2,
								"room": "AUX/ALOCAR"
							}]
						},
						{
							"id": count*10,
							"schedules": [{
								"id": collectionData[count].id,
								"hourStart": collectionData[count].id+3,
								"minuteStart": 0,
								"hourEnd": collectionData[count].id+4,
								"minuteEnd": 30,
								"dayOfWeek": 2,
								"room": "AUX/ALOCAR"
							}]
						}
					])
				]);
			}
			server.autoRespond = true;
			server.autoRespondAfter = 10;
		});
		after(function(){
			server.autoRespond = false;
			server.restore();
		});
		it("Should have the same length as the selected data", function(){
			collection.query();
			var total = 0;
			for(var c=collectionData.length; c--;) {
				if(collectionData[c]._selected) {
					++total;
				}
			}
			expect(collection).to.have.length(total);
		});
		it("Should add a discipline when his turns into a selected discipline", function(){
			collection.live(true);
			expect(collection).to.have.length(3);
			parentCollection.at(0).set({
				"_selected": true
			});
			expect(collection).to.have.length(4);
		});
		describe(".combinationCount()", function(){
			it("Should be a function", function(){
				expect(collection.combinationCount).to.be.a("function");
			});
			it("Should have a total of 8 combinations found", function(){
				return collection.updateCombinations().then(function(){
					expect(collection.combinationCount()).to.be(8);
				})
			});
		});
		describe(".getSelectedCombination", function(){
			it("Should be a function", function(){
				expect(collection.getSelectedCombination).to.be.a("function");
			});
			it("Should return an array", function(){
				return collection.updateCombinations().then(function(){
					var result = collection.getSelectedCombination();
					expect(result).to.be.an("array");
					expect(result).to.have.length(collection.length);
				});
			});
		});
		describe(".getSelectedCombinationNumber", function(){
			it("Should be a function", function(){
				expect(collection.getSelectedCombinationNumber).to.be.a("function");
			});
			it("Should return a number", function(){
				return collection.updateCombinations().then(function(){
					expect(collection.getSelectedCombinationNumber()).to.be.a("number");
				});
			});
		});
		describe(".nextCombination", function(){
			it("Should be a function", function(){
				expect(collection.nextCombination).to.be.a("function");
			});
			it("Should increment the getSelectedCombinationNumber()", function(){
				return collection.updateCombinations().then(function(){
					expect(collection.getSelectedCombinationNumber()).to.be(0);
					collection.nextCombination();
					expect(collection.getSelectedCombinationNumber()).to.be(1);	
				});
			});
		});
		describe(".hasNextCombination", function(){
			it("Should be a function", function(){
				expect(collection.hasNextCombination).to.be.a("function");
			});
			it("Should return a boolean", function(){
				return collection.updateCombinations().then(function(){
					expect(collection.hasNextCombination()).to.be.a("boolean");
				});
			});
		});
		describe(".previousCombination", function(){
			it("Should be a function", function(){
				expect(collection.previousCombination).to.be.a("function");
			});
			it("Should decrement the getSelectedCombinationNumber()", function(){
				return collection.updateCombinations().then(function(){
					collection.nextCombination();
					expect(collection.getSelectedCombinationNumber()).to.be(1);
					collection.previousCombination();
					expect(collection.getSelectedCombinationNumber()).to.be(0);
				});
			});
		});
		describe(".hasPreviousCombination", function(){
			it("Should be a function", function(){
				expect(collection.hasPreviousCombination).to.be.a("function");
			});
			it("Should return a boolean", function(){
				return collection.updateCombinations().then(function(){
					expect(collection.hasPreviousCombination()).to.be.a("boolean");
				});
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