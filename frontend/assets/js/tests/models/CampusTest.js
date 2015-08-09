define("tests/models/CampusTest", [
    "expect",
    "models/CachedModel",
    "models/Campus"
], function(expect, CachedModel, Campus) {
    "use strict";
    describe("models/Campus", function(){
        var model;
        beforeEach(function() {
			model = new Campus();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/campi");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});