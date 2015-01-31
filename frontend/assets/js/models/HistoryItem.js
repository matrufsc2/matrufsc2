define("models/HistoryItem", ["moment", "models/BaseModel"], function(moment, BaseModel) {
    "use strict";
    return BaseModel.extend({
        "defaults": function() {
            return {
                "id": 0,
                "data": {}
            };
        },
		"validator": {
			"type"      : "object",
			"required"  : ["id", "data"],
			"properties": {
				"id": {
					"type": "integer"
				},
				"data": {
					"type": "object"
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