define("collections/Sections", ["collections/PageableCollection", "models/Section"], function (PageableCollection, Section) {
    "use strict";
    return PageableCollection.extend({
        "url": "/api/sections/",
        "model": Section
    });
});