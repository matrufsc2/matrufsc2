define("models/HistoryItem", ["moment", "models/BaseModel"], function(moment, BaseModel) {
    "use strict";
    return BaseModel.extend({
        "defaults": function() {
            return {
                "id": moment.utc().unix(),
                "url": window.location.href
            };
        },
		"validator": {
			"type"      : "object",
			"required"  : ["id", "url"],
			"properties": {
				"id": {
					"type": "integer"
				},
				"url": {
					"type"      : "string"
				}
			}
		},
        "getDate": function(){
            return moment.unix(this.id);
        },
        "getFormattedRelativeDate": function(){
            return this.getDate().calendar(moment.utc());
        },
        "getFormattedDate": function(){
            return this.getDate().format("dddd, D [de] MMMM [de] YYYY [às] HH:mm:ss");
        }
    });
});