define("collections/QuestionsGroups", ["collections/PageableCollection", "models/QuestionsGroup"], function(PageableCollection, QuestionsGroup) {
    "use strict";
    return PageableCollection.extend({
        "url": "/api/questions-groups/",
        "model": QuestionsGroup
    });
});