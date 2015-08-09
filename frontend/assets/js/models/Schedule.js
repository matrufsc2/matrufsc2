define("models/Schedule", ["models/CachedModel"], function (CachedModel) {
    "use strict";
    var hours = ["07:30", "08:20", "09:10", "10:10", "11:00", "13:30", "14:20", "15:10", "16:20", "17:10", "18:30", "19:20", "20:20", "21:10"];
    var daysOfWeek = [null, 0, 1, 2, 3, 4, 5, 6];
    var period = {
        "morning": ["07:30", "08:20", "09:10", "10:10", "11:00"],
        "afternoon": ["13:30", "14:20", "15:10", "16:20", "17:10"],
        "night": ["18:30", "19:20", "20:20", "21:10"]
    };
    function format(date) {
        var hour = "0" + date.getHours();
        var minute = "0" + date.getMinutes();
        return hour.substr(-2, 2) + ":" + minute.substr(-2, 2);
    }

    return CachedModel.extend({
        "defaults": {
            "id": -1,
            "hourStart": 0,
            "minuteStart": 0,
            "numberOfLessons": 0,
            "dayOfWeek": 2,
            "room": "AUX/ALOCAR"
        },
        "conflictsWith": function (schedule) {
            if (schedule.get("dayOfWeek") !== this.get("dayOfWeek")) {
                return false;
            }
            var start1 = this.getStart().getTime();
            var start2 = schedule.getStart().getTime();
            var end1 = this.getEnd().getTime();
            var end2 = schedule.getEnd().getTime();
            return (start2 < end1 || start2 === end1) &&
                (end2 > start1 || end2 === start1);
        },
        "getPeriod": function() {
            var result = [];
            var startRow = this.getStartRow();
            var endRow = this.getEndRow();
            for (var key in period) {
                if (!period.hasOwnProperty(key)) {
                    continue;
                }
                for (var c = startRow; c <= endRow; c++) {
                    var formattedDate = hours[c];
                    if (period[key].indexOf(formattedDate) !== -1 ||
                        period[key].indexOf(formattedDate) !== -1) {
                        if (result.indexOf(key) !== -1) {
                            continue;
                        }
                        result.push(key);
                    }
                }
            }
            return result;
        },
        "getDayOfWeek": function() {
            return daysOfWeek[this.get("dayOfWeek")];
        },
        "getStart": function () {
            var start = new Date(0);
            while (start.getDay() !== this.getDayOfWeek()) {
                start.setDate(start.getDate() + 1);
            }
            start.setHours(this.get("hourStart"), this.get("minuteStart"), 0, 0);
            return start;
        },
        "getStartRow": function () {
            return hours.indexOf(format(this.getStart()));
        },
        "getEndRow": function () {
            return this.getStartRow() + (this.get("numberOfLessons") - 1);
        },
        "getEnd": function () {
            var hourString = hours[this.getEndRow()];
            var hourParts = hourString.split(":");
            var hour = parseInt(hourParts[0]);
            var minute = parseInt(hourParts[1]);

            var end = new Date(0);
            while (end.getDay() !== this.getDayOfWeek()) {
                end.setDate(end.getDate() + 1);
            }
            end.setHours(hour, minute, 0, 0);
            return end;
        }
    });
});