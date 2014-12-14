define("views/FiltersView", [
	"underscore",
	"templates",
	"views/BaseView",
	"diacritic",
	"select2"
], function(_, templates, BaseView, diacritic){
	"use strict";
	var filterCollectionByQuery = function(collection, query, onGet) {
		var count = 0;
		var skip = (query.page-1)*10;
		var limit = skip+11;
		var results = {};
		results.results = _.map(_.filter(collection, function(model){
			if(count >= limit){
				return false;
			}
			var result = onGet(model).toLowerCase().indexOf(diacritic.clean(query.term).toLowerCase()) != -1;
			if(result){
				++count;
			}
			return result && count >= skip;
		}), function(model) {
			return {
				"id": model.id,
				"text": onGet(model)
			};
		});
		results.more = results.results.length === 11;
		results.results = results.results.slice(0, 10);
		return results;
	};
	var getInitSelectionForSelect2 = function(collection, onGet) {
		return function(element, callback) {
			var result = collection.get(element.val());
			if(result) {
				callback({
					"id": result.id,
					"text": onGet(result.toJSON())
				});
			} else {
				callback();
			}
		};
	};
	var FiltersView = BaseView.extend({
		"template" : templates.filters,
		"listen": {
			"render": "applySelect2",
			"addedToDOM": "applyFoundation"
		},
		"initialize": function(options){
			_.extend(this, _.pick(options, ["disciplines", "semesters", "campi", "status"]));
		},
		"applySelect2": function(){
			this.applyFoundation();
			var view = this;
			// Process Semesters..
			var onGetSemester = function(semester) {
				return semester.name;
			};
			this.$("#semester").val(view.status.get("semester")).select2({
				"width": "100%",
				"formatNoMatches": "Nenhum resultado encontrado",
				"formatSearching": "Carregando...",
				"query": function(query) {
					var located = false;
					function doQuery() {
						if (located) {
							return;
						}
						located = true;
						query.callback(filterCollectionByQuery(view.semesters.toJSON(), query, onGetSemester));
					}
					view.semesters.once("synced", doQuery);
					if(view.semesters.isSynced()) {
						doQuery();
					}
				},
				"initSelection": getInitSelectionForSelect2(view.semesters, onGetSemester)
			}).on("change", function(e){
				view.status.set({
					"semester": e.val
				});
			});
			view.listenTo(view.status, "change:semester", function(){
				if(view.status.get("semester") === view.$("#semester").select2("val")){
					return;
				}
				view.$("#semester").select2("val", view.status.get("semester"));
			});

			// Process campus..
			var onGetCampus = function(campus) {
				return campus.name;
			};
			this.$("#campus").val(view.status.get("campus")).select2({
				"width": "100%",
				"formatNoMatches": "Nenhum resultado encontrado",
				"formatSearching": "Carregando...",
				"query": function(query) {
					var located = false;
					function doQuery() {
						if (located) {
							return;
						}
						located = true;
						query.callback(filterCollectionByQuery(view.campi.toJSON(), query, onGetCampus));
					}
					view.campi.once("synced", doQuery);
					if(view.campi.isSynced()) {
						doQuery();
					}
				},
				"initSelection": getInitSelectionForSelect2(view.campi, onGetCampus)
			}).on("change", function(e){
				view.status.set({
					"campus": e.val
				});
			});
			view.listenTo(view.status, "change:campus", function(){
				if(view.status.get("campus") === view.$("#campus").select2("val")){
					return;
				}
				view.$("#campus").select2("val", view.status.get("campus"));
			});

			// Process Disciplines..
			var onGetDiscipline = function(discipline) {
				return discipline.code+" - "+discipline.name;
			};
			this.$("#discipline").select2({
				"width": "100%",
				"formatNoMatches": "Nenhum resultado encontrado",
				"formatSearching": "Carregando...",
				"query": function(query) {
					var located = false;
					function doQuery() {
						if (located) {
							return;
						}
						located = true;
						query.callback(filterCollectionByQuery(view.disciplines.toJSON(), query, onGetDiscipline));
					}
					view.disciplines.once("synced", doQuery);
					if(view.disciplines.isSynced()) {
						doQuery();
					}
				},
				"initSelection": getInitSelectionForSelect2(view.disciplines, onGetDiscipline)
			}).on("select2-selecting", function(e){
				e.preventDefault();
				view.$("#discipline").select2("close");
				var discipline = view.disciplines.get(e.val);
				if(!discipline) {
					alert("Disciplina nao encontrada!");
					return;
				}
				discipline.select();
			});
		}
	});
	return FiltersView;
});