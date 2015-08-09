define("tests/models/PostTest", [
    "expect",
    "models/CachedModel",
    "models/Post"
], function(expect, CachedModel, Post) {
    "use strict";
    describe("models/Post", function(){
        var model;
        beforeEach(function() {
			model = new Post();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/posts/");
            });
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});