define("tests/models/TeacherTest", [
    "expect",
    "models/CachedModel",
    "models/Teacher"
], function(expect, CachedModel, Teacher) {
    "use strict";
    describe("models/Teacher", function(){
        var model;
        beforeEach(function() {
			model = new Teacher();
        });
        it("Is an instance of CachedModel", function() {
            expect(model).to.be.a(CachedModel);
        })
    });
});