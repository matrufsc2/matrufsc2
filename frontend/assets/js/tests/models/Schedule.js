define("tests/models/Schedule", ["expect", "underscore", "models/Schedule"], function(expect, _, Schedule) {
	"use strict";
	describe("Schedule", function(){
		var model;
		beforeEach(function(){
			model = new Schedule({
				"id": -1,
				"hourStart": 0,
				"minuteStart": 0,
				"hourEnd": 0,
				"minuteEnd": 0,
				"dayOfWeek": 2,
				"room": "EFI503"
			});
		});
		it("Should put default valid values when not present", function(){
			model = new Schedule();
			model.set({"id": 2});
			expect(model.get("hourStart")).to.be(0);
			expect(model.get("minuteStart")).to.be(0);
			expect(model.get("hourEnd")).to.be(0);
			expect(model.get("minuteEnd")).to.be(0);
			expect(model.get("dayOfWeek")).to.be(2);
			expect(model.get("room")).to.be("AUX/ALOCAR");
			expect(model.validate()).to.be(undefined);
		});
		it("Should validate the models correctly", function(){
			expect(model.validate()).to.be(undefined);
			model.unset("hourStart");
			expect(model.validate()).to.not.be(undefined);
		});
	});
});