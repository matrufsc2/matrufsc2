define("tests/models/PageTest", [
    "expect",
    "models/CachedModel",
    "models/Page"
], function(expect, CachedModel, Page) {
    "use strict";
    describe("models/Page", function(){
        var model;
        beforeEach(function() {
			model = new Page();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/pages/");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});