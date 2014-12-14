define("views/BaseView", ["underscore", "chaplin", "foundation"], function(_, Chaplin) {
  "use strict";
  var BaseView = Chaplin.View.extend({
    "autoRender": true,
    "listen": {
      "addedToDOM": "applyFoundation"
    },
    "getTemplateFunction": function(){
      var template = this.template;
      if(!_.isFunction(template)){
        template = function(){
          return "";
        };
      }
      return template;
    },
    "render": function(){
      Chaplin.View.prototype.render.apply(this, []);
      this.attach();
      this.trigger("render");
    },
    "applyFoundation": function(){
      this.$el.foundation();
    }
  });
  return BaseView;
});