define("collections/Articles", [
    "collections/PageableSearchableCollection",
    "models/Article"
], function (PageableSearchableCollection, Article) {
    "use strict";
    return PageableSearchableCollection.extend({
        "url": "/api/articles/",
        "model": Article
    });
});