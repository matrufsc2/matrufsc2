var cssurl = require("cssurl");
var translator = new cssurl.URLTranslator();
exports.config = {
  "modules": [
    "copy",
    "server",
    "jshint",
    "csslint",
    "require",
    "minify-js",
    "minify-css",
    "live-reload",
    "bower",
    "underscore",
    "combine",
    "web-package"
  ],
  "server": {
    "views": {
      "compileWith" : "html",
      "extension"   : "html"
    },
    "defaultServer": {
      "enabled": true
    }
  },
  "watch": {
    "javascriptDir": "js"
  },
  "vendor": {
    "javascripts" : "js/vendor",
    "stylesheets" : "css/vendor"
  },
  "template": {
    "outputFileName" : "js/templates",
    "wrapType"       : "amd"
  },
  "require": {
    "commonConfig" : "config",
    "optimize"     : {
      "overrides": {
         "include"        : [
            "boot",
            "controllers/AboutController",
            "controllers/HomeController"
          ],
          "insertRequire" : ["boot"],
          "out"           : "main.js",
          "generateSourceMaps": true,
          "preserveLicenseComments": false
      }
    }
  },
  "bower": {
    "bowerDir": {
      "path": ".mimosa/bower/bower_components",
      "clean": false
    },
    "copy": {
      "mainOverrides": {
        "mocha"     : ["mocha.js", "mocha.css"],
        "modernizr" : ["modernizr.js"],
        "moment"    : ["moment.js", "lang/pt-br.js"],
        "expect"    : ["index.js"],
        "pleasejs"  : ["dist/Please.js"],
        "diacritic": ["diacritics.js"]
      }
    }
  },
  "combine": {
    "folders": [{
      "folder"  : "css/",
      "output"  : "css/main.css",
      "exclude" : ["vendor/mocha/mocha.css", "vendor/foundation/foundation.css.map"],
      "order"   : null,
      "transforms": [function(inputText,inputName,outputName) {
        "use strict";
        var rewriter = new cssurl.URLRewriter(function(url) {
          return translator.translate(url, inputName, outputName);
        });
        return rewriter.rewrite(inputText);
      }]
    }],
    "removeCombined": {
      "enabled" : true,
      "exclude" : []
    }
  }
};