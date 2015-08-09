define("tests/collections/TeachersTest", [
    "expect",
    "collections/Teachers",
    "collections/CachedCollection",
    "models/Teacher"
], function(expect, Teachers, CachedCollection, Teacher) {
    "use strict";
    describe("collections/Teachers", function(){
        var collection;
        beforeEach(function() {
			collection = new Teachers();
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Teacher);
            });
        });
        it("Is an instance of CachedCollection", function() {
            expect(collection).to.be.a(CachedCollection);
        })
    });
});