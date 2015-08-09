define("tests/collections/CampiTest", [
    "expect",
    "collections/Campi",
    "collections/CachedCollection",
    "models/Campus"
], function(expect, Campi, CachedCollection, Campus) {
    "use strict";
    describe("collections/Campi", function(){
        var collection;
        beforeEach(function() {
			collection = new Campi();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/campi/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Campus);
            });
        });
        it("Is an instance of CachedCollection", function() {
            expect(collection).to.be.a(CachedCollection);
        })
    });
});