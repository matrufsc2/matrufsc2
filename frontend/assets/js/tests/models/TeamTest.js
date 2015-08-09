define("tests/models/TeamTest", [
    "expect",
    "models/CachedModel",
    "models/Team"
], function(expect, CachedModel, Team) {
    "use strict";
    describe("models/Team", function(){
        var model;
        beforeEach(function() {
			model = new Team();
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});