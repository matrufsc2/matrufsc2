define("controllers/QuestionsGroupsController", [
    "underscore",
    "backbone",
    "controllers/BaseController",
    "collections/QuestionsGroups",
    "views/QuestionsGroupsView"
], function (_, Backbone, BaseController, QuestionsGroups, QuestionsGroupsView) {
    "use strict";
    return BaseController.extend({
        "index": function (params, metadata, request) {
            this.adjustTitle("Perguntas Frequentes");
            this.collection = new QuestionsGroups();
            this.collection.currentPage = parseInt(request.query.page, 10) || 1;
            this.view = new QuestionsGroupsView({
                "collection": this.collection
            });
            this.collection.fetch();
        }
    });
});
