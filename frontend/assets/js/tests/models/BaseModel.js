define("tests/models/BaseModel", ["expect", "underscore", "sinon", "models/BaseModel"], function(expect, _, sinon, BaseModel) {
	"use strict";
	describe("BaseModel", function(){
		var model, modelData = {
			"id": 2,
			"name": "Foo",
			"property" : "Bar"
		};
		beforeEach(function(){
			model = new BaseModel(modelData);
		});
		it("Should validate the models correctly", function(){
			model.validator= {
				"type"       : "object",
				"required"   : ["id", "name", "property"],
				"properties" : {
					"id"   : {
						"type" : "integer"
					},
					"name" : {
						"type"      : "string",
						"minLength" : 2
					},
					"property" : {
						"type"      : "string",
						"minLength" : 2
					},
				}
			};
			expect(model.validate()).to.be(undefined);
			model.unset("property");
			expect(model.validate()).to.not.be(undefined);
		});
		it("Should throw when detect missing schemas automatically", function(){
			model.validator= {
				"type"       : "object",
				"required"   : ["id", "name", "property"],
				"properties" : {
					"id"   : {
						"type" : "integer"
					},
					"name" : {
						"type"      : "string",
						"minLength" : 2
					},
					"property" : {
						"$ref" : "schema"
					}
				}
			};
			expect(function(){
				model.validate();
			}).to.throwError(/Missing schemas detected. Please fix it to do perfect validation: .*/);
		});
		describe(".fetch()", function(){
			var server;
			beforeEach(function(){
				server = sinon.fakeServer.create();
				model.clear();
				model.url = "/foo/bar";
			});
			afterEach(function(){
				server.restore();
			});
			it("Should be capable of downloading the data correctly", function(done){
				model.fetch().then(function(){
					expect(model.toJSON()).to.eql(modelData);
					done();
				}, function(err){
					done(err.thrown);
				});
				server.respondWith([
					200,
					{ "Content-Type": "application/json" },
					JSON.stringify(modelData)
				]);
				server.respond();
			});
			it("Should be capable of emit an error when the download fails", function(done){
				model.fetch().then(function(){
					done(new Error("Unexpected Success"));
				}, function(){
					expect(model.toJSON()).to.eql({});
					done();
				});
				server.respondWith([
					404,
					{ "Content-Type": "application/json" },
					""
				]);
				server.respond();
			});
			it("Should be capable of fetch data without specify callbacks", function(done){
				model.on("sync", function(){
					expect(model.toJSON()).to.eql(modelData);
					done();
				});
				model.fetch();
				server.requests[0].respond(
					200,
					{ "Content-Type": "application/json" },
					JSON.stringify(modelData)
				);
			});
		});
	});
});