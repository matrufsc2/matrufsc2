define("views/FiltersView", [
	"underscore",
	"templates",
	"views/BaseView",
	"models/Discipline",
	"diacritic",
	"select2"
], function(_, templates, BaseView, Discipline, diacritic){
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
			_.extend(this, _.pick(options, ["selectedDisciplines", "semesters", "campi", "status"]));
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
			view.listenTo(view.status, "change:semester", function updateSemestersFilter(){
                if (!view.semesters.length) {
                    return setTimeout(updateSemestersFilter, 100);
                }
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
			view.listenTo(view.status, "change:campus", function updateCampusFilter(){
                if (!view.campi.length) {
                    return setTimeout(updateCampusFilter, 100);
                }
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
				"formatNoMatches": "Nenhum resultado encontrado :(",
				"formatSearching": "Carregando, aguarde...",
				"formatLoadMore": "Carregando mais resultados..",
				"loadMorePadding": 20,
				"nextSearchTerm": function(selectedObject, currentSearchTerm) {
					return currentSearchTerm;
				},
				"ajax":  {
					url: Discipline.prototype.urlRoot,
					dataType: 'json',
					quietMillis: 250,
					cache: true,
					data: function (term, page) {
						return {
							"q": diacritic.clean(term),
							"page": page,
							"campus": view.status.get("campus")
						};
					},
					results: function (data, page, query) {
						var results = {
							"more": data.more,
							"results": []
						};
						var r = data.results;
						for (var i = 0, l = r.length; i < l; i++) {
							if (view.selectedDisciplines.get(r[i].id)) {
								continue;
							}
							var text = onGetDiscipline(r[i]);
							var result = text.toLowerCase().indexOf(diacritic.clean(query.term).toLowerCase()) != -1;
							if (result) {
								results.results.push({
									"id": r[i].id,
									"text": text,
									"original": r[i]
								});
							}
						}
						return results;
					}
				}
			}).on("select2-selecting", function(e){
				e.preventDefault();
				view.$("#discipline").select2("close");
				var discipline = e.choice;
				if(!discipline) {
					alert("Disciplina nao encontrada!");
					return;
				}
				discipline = new Discipline(discipline.original);
				view.selectedDisciplines.add(discipline);
				discipline.select();
			});
		}
	});
	return FiltersView;
});