var cssurl = require("cssurl");
var translator = new cssurl.URLTranslator();
exports.config = {
    "modules": [
        "copy",
        "server",
        "jshint",
        "csslint",
        "require",
        "minify-css",
        "live-reload",
        "bower",
        "underscore",
        "combine",
        "web-package"
    ],
    "server": {
        "views": {
            "compileWith": "html",
            "extension": "html"
        },
        "defaultServer": {
            "enabled": true
        }
    },
    "watch": {
        "javascriptDir": "js"
    },
    "vendor": {
        "javascripts": "js/vendor",
        "stylesheets": "css/vendor"
    },
    "logger": {
        "success": {
            "enabled": false
        }
    },
    "template": {
        "outputFileName": "js/templates",
        "wrapType": "amd"
    },
    "require": {
        "commonConfig": "config",
        "optimize": {
            "overrides": {
                "include": [
                    "boot",
                    "controllers/AboutController",
                    "controllers/HomeController"
                ],
                "insertRequire": ["boot"],
                "out": "main.js",
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
                // "jquery": ["src/"],
                "mocha": ["mocha.js", "mocha.css"],
                "modernizr": ["modernizr.js"],
                "moment": ["moment.js", "lang/pt-br.js"],
                "expect": ["index.js"],
                "pleasejs": ["dist/Please.js"],
                "foundation": ["css/foundation.css", "js/foundation/foundation.js",
                    "js/foundation/foundation.accordion.js", "js/foundation/foundation.joyride.js",
                    "js/foundation/foundation.topbar.js",
                    "js/foundation/foundation.dropdown.js", "js/foundation/foundation.tooltip.js",
                    "js/foundation/foundation.reveal.js", "js/foundation/foundation.equalizer.js"]
            }
        }
    },
    "combine": {
        "folders": [{
            "folder": "css/",
            "output": "css/main.css",
            "exclude": ["vendor/mocha/mocha.css", "vendor/foundation/foundation.css.map"],
            "order": null,
            "transforms": [function (inputText, inputName, outputName) {
                "use strict";
                var rewriter = new cssurl.URLRewriter(function (url) {
                    return translator.translate(url, inputName, outputName);
                });
                return rewriter.rewrite(inputText);
            }]
        }],
        "removeCombined": {
            "enabled": true,
            "exclude": []
        }
    }
};