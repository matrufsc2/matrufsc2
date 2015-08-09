define("tests/collections/SectionsTest", [
    "expect",
    "collections/Sections",
    "collections/PageableCollection",
    "models/Section"
], function(expect, Sections, PageableCollection, Section) {
    "use strict";
    describe("collections/Sections", function(){
        var collection;
        beforeEach(function() {
			collection = new Sections();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/sections/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Section);
            });
        });
        it("Is an instance of PageableCollection", function() {
            expect(collection).to.be.a(PageableCollection);
        })
    });
});