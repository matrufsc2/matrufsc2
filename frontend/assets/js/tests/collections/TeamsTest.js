define("tests/collections/TeamsTest", [
    "expect",
    "collections/Teams",
    "collections/CachedCollection",
    "models/Team"
], function(expect, Teams, CachedCollection, Team) {
    "use strict";
    describe("collections/Teams", function(){
        var collection;
        beforeEach(function() {
			collection = new Teams();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/teams/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Team);
            });
        });
        it("Is an instance of CachedCollection", function() {
            expect(collection).to.be.a(CachedCollection);
        })
    });
});