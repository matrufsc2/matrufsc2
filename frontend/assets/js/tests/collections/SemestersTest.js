define("tests/collections/SemestersTest", [
    "expect",
    "collections/Semesters",
    "collections/CachedCollection",
    "models/Semester"
], function(expect, Semesters, CachedCollection, Semester) {
    "use strict";
    describe("collections/Semesters", function(){
        var collection;
        beforeEach(function() {
			collection = new Semesters();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/semesters/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Semester);
            });
        });
        it("Is an instance of CachedCollection", function() {
            expect(collection).to.be.a(CachedCollection);
        })
    });
});