define(["application", "routes", "moment", "moment-pt-br"], function(Application, routes, moment) {
  moment.lang("pt-br", {
    calendar : {
        sameDay: '[Hoje às] LT',
        nextDay: '[Amanhã às] LT',
        nextWeek: 'dddd [às] LT',
        lastDay: '[Ontem às] LT',
        lastWeek: function () {
            return (this.day() === 0 || this.day() === 6) ?
                '[Último] dddd [às] LT' : // Saturday + Sunday
                '[Última] dddd [às] LT'; // Monday - Friday
        },
        sameElse: 'L [às] LT'
    }
  });
  return new Application({
	routes: routes
  });
});