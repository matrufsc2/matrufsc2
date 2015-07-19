define("collections/Posts", [
    "chaplin",
    "collections/PageableSearchableCollection",
    "models/Post"
], function (Chaplin, PageableSearchableCollection, Post) {
    "use strict";
    return PageableSearchableCollection.extend({
        "url": "/api/posts/",
        "model": Post
    });
});