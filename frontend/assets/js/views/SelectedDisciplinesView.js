define("views/SelectedDisciplinesView", [
		"templates",
		"views/BaseView",
		"chaplin",
		"underscore",
		"views/SelectedDisciplineView"
], function(templates, BaseView, Chaplin, _, selectedDisciplineView){
	"use strict";
	var SelectedDisciplinesView = BaseView.extend({
		"template" : templates.selectedDisciplines,
		"itemView": selectedDisciplineView,
		"listSelector": "tbody",
		"tagName": "table",
		"listen": {
      		"addedToDOM": "applyFoundation",
      		"change:combination collection": "updateViews",
      		"sort collection": "renderAllItems"
		},
		"events": {
			"click #nextCombination": "nextCombination",
			"click #previousCombination": "previousCombination"
		},
		"initialize": function(options){
			_.extend(this, _.pick(options, "status"));
			BaseView.prototype.initialize.apply(this, [options]);
			Chaplin.CollectionView.prototype.initialize.apply(this, [options]);
		},
		"updateViews": function(){
			this.collection.each(function(discipline) {
				this.renderItem(discipline); // Forces update of the view
			}, this);
			this.updateCombinationStatus();
			this.updateTotalHours();
		},
		"updateCombinationStatus": function(){
			this.$("#combinationStatus").html(this.getCombinationStatus());
		},
		"updateTotalHours": function(){
			this.$("#totalHours").html(this.getTotalHours());
		},
		"getTotalHours": function() {
			return this.collection.reduce(function(total, discipline){
				return total + (discipline.team ? discipline.team.getNumberOfLessons() : 0);
			}, 0);
		},
		"getCombinationStatus": function(){
			var combinationTotal, combinationNumber;
			combinationTotal = this.collection.combinationCount();
			combinationNumber = combinationTotal > 0 ? this.collection.getSelectedCombination()+1 : 0;
			return combinationNumber+"/"+combinationTotal;
		},
		"nextCombination": function(e){
			this.collection.nextCombination();
			e.preventDefault();
		},
		"previousCombination": function(e){
			this.collection.previousCombination();
			e.preventDefault();
		},
		"initItemView": function(model){
			if (this.itemView) {
				return new this.itemView({
					"autoRender": false,
					"model": model,
					"status": this.status
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
		"render": function(){
			BaseView.prototype.render.apply(this, []);
			Chaplin.CollectionView.prototype.render.apply(this, []);
			this.updateCombinationStatus();
			this.updateTotalHours();
		}
	});
	_.extend(SelectedDisciplinesView.prototype,
		_.omit(
			Chaplin.CollectionView.prototype,
			_.keys(SelectedDisciplinesView.prototype),
			_.keys(BaseView.prototype)
		)
	);
	return SelectedDisciplinesView;
});