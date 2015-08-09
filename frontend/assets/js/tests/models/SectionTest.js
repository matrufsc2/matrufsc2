define("tests/models/SectionTest", [
    "expect",
    "models/CachedModel",
    "models/Section"
], function(expect, CachedModel, Section) {
    "use strict";
    describe("models/Section", function(){
        var model;
        beforeEach(function() {
			model = new Section();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/sections/");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});