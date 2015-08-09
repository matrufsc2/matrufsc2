define("tests/models/SemesterTest", [
    "expect",
    "models/CachedModel",
    "models/Semester"
], function(expect, CachedModel, Semester) {
    "use strict";
    describe("models/Semester", function(){
        var model;
        beforeEach(function() {
			model = new Semester();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/semesters/");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});