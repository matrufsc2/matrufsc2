define("views/BaseView", ["underscore", "chaplin", "fastdom", "foundation"], function(_, Chaplin, fastdom) {
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
      fastdom.write(function(){
        Chaplin.View.prototype.render.apply(this, []);
        this.attach();
        this.trigger("render");
      }, this);
    },
    "applyFoundation": function(){
        fastdom.write(function(){
          this.$el.foundation();
        }, this);
    }
  });
  return BaseView;
});