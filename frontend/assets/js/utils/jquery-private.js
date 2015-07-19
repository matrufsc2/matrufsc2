define(["jquery"], function (jq) {
    "use strict";
    // Little Hack to get jQuery without polluting global vars
    return jq.noConflict(false); // Note that we cannot remove jQuery from global scope because Foundation needs it
});
