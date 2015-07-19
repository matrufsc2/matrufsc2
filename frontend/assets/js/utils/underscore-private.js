define(["underscore"], function (underscore) {
    "use strict";
    // Little Hack to get Underscore without polluting global vars
    return underscore.noConflict();
});
