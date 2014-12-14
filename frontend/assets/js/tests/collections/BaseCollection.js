define("tests/collections/BaseCollection", ["expect", "sinon", "collections/BaseCollection"], function(expect, sinon, BaseCollection) {
	"use strict";
	describe("BaseCollection", function(){
		var collection, collectionData = [{
			"id": 3
		}, {
			"id": 5
		}];
		beforeEach(function(){
			collection = new BaseCollection();
			collection.add(collectionData);
		});
		it("Should have the same length as the original data", function(){
			expect(collection).to.have.length(collectionData.length);
		});
		describe(".fetch()", function(){
			var server;
			beforeEach(function(){
				server = sinon.fakeServer.create();
				collection.reset();
			});
			afterEach(function(){
				server.restore();
			});
			it("Should be capable of downloading the data correctly", function(done){
				collection.fetch().then(function(){
					expect(collection).to.have.length(collectionData.length);
					done();
				},function(err){
					done(err.thrown);
				});
				server.requests[0].respond(
					200,
					{ "Content-Type": "application/json" },
					JSON.stringify(collectionData)
				);
			});
			it("Should be capable of emit an error when the download fails", function(done){
				collection.fetch().then(function(){
					done(new Error("Unexpected Success"));
				}, function(){
					expect(collection).to.have.length(0);
					done();
				});
				server.requests[0].respond(
					404,
					{ "Content-Type": "application/json" }
				);
			});
			it("Should be capable of fetch without specify callbacks", function(done){
				collection.on("sync", function(){
					expect(collection.toJSON()).to.have.length(collectionData.length);
					done();
				});
				collection.fetch();
				server.requests[0].respond(
					200,
					{ "Content-Type": "application/json" },
					JSON.stringify(collectionData)
				);
			});
		});
	});
});