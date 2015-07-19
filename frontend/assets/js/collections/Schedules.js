define("collections/Schedules", ["collections/CachedCollection", "models/Schedule", "underscore"], function (CachedCollection, Schedule, _) {
    "use strict";
    var hours = ["07:30", "08:20", "09:10", "10:10", "11:00", "13:30", "14:20", "15:10", "16:20", "17:10", "18:30", "19:20", "20:20", "21:10"];
    var getStartRow = function (schedule) {
        return schedule.getStartRow();
    };
    return CachedCollection.extend({
        "model": Schedule,
        "compact": function () {
            // Compact the schedules, resuming to the less schedules possible :D
            var schedulesByDayOfWeek = this.groupBy("dayOfWeek");
            var schedule = null;
            var result = [];
            var i, dayOfWeek;
            for (dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
                if (!schedulesByDayOfWeek[dayOfWeek]) {
                    continue;
                }
                var schedules = _.sortBy(schedulesByDayOfWeek[dayOfWeek], getStartRow);
                schedule = null;
                for (i = 0; i < schedules.length; ++i) {
                    if (schedule === null) {
                        schedule = schedules[i].clone();
                    }
                    else if (schedule.getEndRow() === (schedules[i].getStartRow() - 1)) {
                        schedule.set({
                            "numberOfLessons": schedule.get("numberOfLessons") + 1
                        });
                    } else {
                        result.push(schedule);
                        schedule = schedules[i].clone();
                    }
                }
                if (schedule !== null) {
                    result.push(schedule);
                }
            }
            this.reset();
            this.set(result);
        },
        "descompact": function () {
            // Descompact the schedules, resuming to the less schedules possible :D
            var scheduleClone, endRow, j, hour;
            var result = [];
            this.each(function (schedule) {
                endRow = schedule.getEndRow();
                for (j = schedule.getStartRow(); j <= endRow; ++j) {
                    scheduleClone = schedule.clone();
                    hour = hours[j].split(":");
                    scheduleClone.set({
                        "id": _.uniqueId("schedule"),
                        "hourStart": parseInt(hour[0]),
                        "minuteStart": parseInt(hour[1]),
                        "numberOfLessons": 1
                    });
                    result.push(scheduleClone);
                }
            });
            this.reset();
            this.set(result);
        },
        "getNumberOfLessons": function () {
            return this.reduce(function (total, schedule) {
                return total + schedule.get("numberOfLessons");
            }, 0);
        }
    });
});