define(["application", "routes", "moment"], function(Application, routes, moment) {
  moment.lang("pt");
  return new Application({
	routes: routes
  });
});