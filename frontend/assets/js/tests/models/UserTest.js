define("tests/models/UserTest", [
    "expect",
    "models/BaseModel",
    "models/User"
], function(expect, BaseModel, User) {
    "use strict";
    describe("models/User", function(){
        var model;
        beforeEach(function() {
			model = new User();
        });
        describe("#urlRoot", function() {
            it("Should point to correct API endpoint", function() {
                expect(model.urlRoot).to.be.equal("/api/users/");
            });
        });
        describe("#defaults", function() {
            it("Should load as not authenticated", function() {
                expect(model.defaults.is_authenticated).to.be.equal(false);
            });
            it("Should not have login url defined", function() {
                expect(model.defaults.login_url).to.be.equal(null);
            });
            it("Should not have logout url defined", function() {
                expect(model.defaults.logout_url).to.be.equal(null);
            });
        })
        it("Is an instance of BaseModel", function() {
            expect(model).to.be.a(BaseModel);
        })
    });
});