define("tests/models/ArticleTest", [
    "expect",
    "models/CachedModel",
    "models/Article"
], function(expect, CachedModel, Article) {
    "use strict";
    describe("models/Article", function(){
        var model;
        beforeEach(function() {
			model = new Article();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/articles/");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});