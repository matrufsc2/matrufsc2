define("tests/collections/CategoriesTest", [
    "expect",
    "collections/Categories",
    "collections/PageableCollection",
    "models/Category"
], function(expect, Categories, PageableCollection, Category) {
    "use strict";
    describe("collections/Categories", function(){
        var collection;
        beforeEach(function() {
			collection = new Categories();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/categories/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Category);
            });
        });
        it("Is an instance of PageableCollection", function() {
            expect(collection).to.be.a(PageableCollection);
        })
    });
});