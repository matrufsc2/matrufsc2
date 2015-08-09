define("tests/collections/PostsTest", [
    "expect",
    "collections/Posts",
    "collections/PageableSearchableCollection",
    "models/Post"
], function(expect, Posts, PageableSearchableCollection, Post) {
    "use strict";
    describe("collections/Posts", function(){
        var collection;
        beforeEach(function() {
			collection = new Posts();
        });
        describe("#url", function() {
            it("Should point to correct API endpoint", function() {
                expect(collection.url).to.be.equal("/api/posts/");
            });
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Post);
            });
        });
        it("Is an instance of PageableSearchableCollection", function() {
            expect(collection).to.be.a(PageableSearchableCollection);
        })
    });
});