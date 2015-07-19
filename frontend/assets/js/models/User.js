define("models/User", ["models/BaseModel"], function (BaseModel) {
    "use strict";
    return BaseModel.extend({
        "urlRoot": "/api/users/",
        "defaults": {
            "is_authenticated": false,
            "login_url": null,
            "logout_url": null
        }
    });
});