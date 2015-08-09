define("tests/collections/PlansTest", [
    "expect",
    "collections/Plans",
    "collections/BaseCollection",
    "models/Plan"
], function(expect, Plans, BaseCollection, Plan) {
    "use strict";
    describe("collections/Plans", function(){
        var collection;
        beforeEach(function() {
			collection = new Plans();
        });
        describe("#model", function() {
            it("Should point to correct model class", function() {
                expect(collection.model).to.be.equal(Plan);
            });
        });
        it("Is an instance of BaseCollection", function() {
            expect(collection).to.be.a(BaseCollection);
        })
    });
});