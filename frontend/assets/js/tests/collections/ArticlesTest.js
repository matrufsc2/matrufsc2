define("tests/collections/ArticlesTest", [
    "expect",
    "collections/Articles",
    "collections/PageableSearchableCollection",
    "models/Article"
], function(expect, Articles, PageableSearchableCollection, Article) {
    "use strict";
    describe("collections/Articles", function(){
        var collection;
        beforeEach(function() {
            collection = new Articles();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/articles/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Article);
            });
        });
        it("Is an instance of PageableSearchableCollection", function() {
            expect(collection).to.be.a(PageableSearchableCollection);
        })
    });
});