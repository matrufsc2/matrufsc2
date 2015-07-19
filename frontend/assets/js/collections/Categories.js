define("collections/Categories", ["collections/PageableCollection", "models/Category"], function (PageableCollection, Category) {
    "use strict";
    return PageableCollection.extend({
        "url": "/api/categories/",
        "model": Category
    });
});