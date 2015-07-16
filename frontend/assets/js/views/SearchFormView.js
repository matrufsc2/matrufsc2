define("views/SearchFormView", ["views/BaseView", "templates"], function (BaseView, templates) {
    "use strict";
    return BaseView.extend({
        "template": templates.searchForm,
        "events": {
            "submit form": "search"
        },
        "search": function(e) {
            this.collection.search(this.$("#q").val());
            e.preventDefault();
        },
        "getTemplateData": function() {
            return {
                "q": this.collection.getQuery()
            };
        }
    });
});