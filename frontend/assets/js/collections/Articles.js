define("collections/Articles", [
    "underscore",
    "chaplin",
    "collections/PageableSearchableCollection",
    "models/Article"
], function(_, Chaplin, PageableSearchableCollection, Article) {
    "use strict";
    return PageableSearchableCollection.extend({
        "url": "/api/articles/",
        "model": Article
    });
});