define("tests/models/CategoryTest", [
    "expect",
    "models/CachedModel",
    "models/Category"
], function(expect, CachedModel, Category) {
    "use strict";
    describe("models/Category", function(){
        var model;
        beforeEach(function() {
			model = new Category();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/categories/");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});