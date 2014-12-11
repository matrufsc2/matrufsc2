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
          "out"           : "main.js"
      }
    }
  },
  "bower": {
    "copy": {
      "mainOverrides": {
        "mocha"     : ["mocha.js", "mocha.css"],
        "modernizr" : ["modernizr.js"],
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
      "exclude" : ["vendor/mocha/mocha.css"],
      "order"   : null
    }],
    "removeCombined": {
      "enabled" : true,
      "exclude" : []
    }
  }
};