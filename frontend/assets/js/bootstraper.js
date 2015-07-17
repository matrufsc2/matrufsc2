define(["application", "routes", "es6-promise"], function (Application, routes, Promise) {
    "use strict";
    Promise.polyfill();
    return new Application({
        routes: routes
    });
});