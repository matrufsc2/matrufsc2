define(["backbone"], function (Backbone) {
    "use strict";
    // Little Hack to get Underscore without polluting global vars
    return Backbone.noConflict();
});
