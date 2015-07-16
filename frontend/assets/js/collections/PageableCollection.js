define("collections/PageableCollection", ["chaplin"], function(Chaplin) {
    "use strict";
    return Chaplin.Collection.extend({
        "totalPages": 0,
        "currentPage": 1,
        "parse": function (response) {
            this.totalPages = response.total_pages;
            this.currentPage = response.page;
            if (this.totalPages > 0 && this.totalPages < this.currentPage) {
                this.currentPage = 1;
                this.fetch();
                return [];
            }
            return response.results;
        },
        "fetch": function(options) {
            options = options || {};
            options.data = options.data || {};
            options.data.page = this.currentPage;
            return Chaplin.Collection.prototype.fetch.call(this, options);
        },
        "nextPage": function() {
            if (this.currentPage >= this.totalPages) {
                return;
            }
            this.currentPage++;
            this.fetch();
        },
        "previousPage": function() {
            if (this.currentPage <= 1) {
                return;
            }
            this.currentPage--;
            this.fetch();
        },
        "goToPage": function(page) {
            if (page > this.totalPages || page < 1) {
                return;
            }
            this.currentPage = page;
            this.fetch();
        },
        "goToFirstPage": function() {
            this.currentPage = 1;
            this.fetch();
        },
        "goToLastPage": function() {
            this.currentPage = this.totalPages;
            this.fetch();
        }
    });
});