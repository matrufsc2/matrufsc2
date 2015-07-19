define("views/PaginationView", [
    "underscore",
    "jquery",
    "templates",
    "views/BaseView"
], function (_, $, templates, BaseView) {
    "use strict";
    return BaseView.extend({
        "template": templates.pagination,
        "listen": {
            "changePage collection": "render"
        },
        "events": {
            "click .last-page:not(.unavailable) a": "goToLastPage",
            "click .first-page:not(.unavailable) a": "goToFirstPage",
            "click .go-to-page a": "goToPage",
            "click .current a": "prevent"
        },
        "showPrevious": 4,
        "showNext": 4,
        "showEnd": 4,
        "showFirst": 4,
        "goToLastPage": function (e) {
            this.collection.goToLastPage();
            this.prevent(e);
        },
        "goToFirstPage": function (e) {
            this.collection.goToFirstPage();
            this.prevent(e);
        },
        "goToPage": function (e) {
            this.collection.goToPage($(e.currentTarget).html());
            this.prevent(e);
        },
        "prevent": function (e) {
            e.preventDefault();
        },
        "getNextPagesLength": function (consider_previous) {
            var previous = 0;
            if (consider_previous === true) {
                previous = this.showPrevious + this.getPreviousPagesLength(false);
            }
            var max = this.collection.currentPage + this.showNext + previous;
            if (max > this.collection.totalPages) {
                max = this.collection.totalPages;
            }
            return max - this.collection.currentPage;
        },
        "getPreviousPagesLength": function (consider_next) {
            var next = 0;
            if (consider_next === true) {
                next = this.showNext - this.getNextPagesLength(false);
            }
            var min = this.collection.currentPage - (this.showPrevious + next);
            if (min < 1) {
                min = 1;
            }
            return min - this.collection.currentPage;
        },
        "getPreviousPages": function () {
            var min = this.collection.currentPage + this.getPreviousPagesLength(true);
            var result = [];
            for (var c = min; c < this.collection.currentPage; c++) {
                result.push(c);
            }
            return result;
        },
        "getNextPages": function () {
            var max = this.collection.currentPage + this.getNextPagesLength(true);
            var result = [];
            for (var c = this.collection.currentPage + 1; c <= max; c++) {
                result.push(c);
            }
            return result;
        },
        "getEndPages": function () {
            if (this.collection.currentPage >= this.collection.totalPages - this.showEnd - this.showNext - 1) {
                return [];
            }
            var result = [];
            for (var c = this.collection.totalPages - this.showEnd + 1; c <= this.collection.totalPages; c++) {
                result.push(c);
            }
            return result;
        },
        "getFirstPages": function () {
            if (this.collection.currentPage <= this.showFirst + this.showPrevious + 1) {
                return [];
            }
            var result = [];
            for (var c = 1; c <= this.showFirst; c++) {
                result.push(c);
            }
            return result;
        },
        "getFirstItemClass": function () {
            return this.getFirstPages().length === 0 ? "unavailable" : "";
        },
        "getLastItemClass": function () {
            return this.getEndPages().length === 0 ? "unavailable" : "";
        },
        "getTemplateData": function () {
            return {
                "previousPages": this.getPreviousPages(),
                "nextPages": this.getNextPages(),
                "firstPages": this.getFirstPages(),
                "endPages": this.getEndPages(),
                "currentPage": this.collection.currentPage,
                "firstItemClass": this.getFirstItemClass(),
                "lastItemClass": this.getLastItemClass()
            };
        }
    });
});