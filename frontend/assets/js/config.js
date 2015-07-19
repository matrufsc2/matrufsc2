require.config({
    "baseUrl": "/js/",
    "paths": {
        "jquery": "vendor/jquery/jquery",
        "underscore": "vendor/underscore/underscore",
        "backbone": "vendor/backbone/backbone",
        "chaplin": "vendor/chaplin/chaplin",
        "es5-shim": "vendor/es5-shim/es5-shim",
        "foundation": "vendor/foundation/foundation",
        "foundation-accordion": "vendor/foundation/foundation.accordion",
        "foundation-tooltip": "vendor/foundation/foundation.tooltip",
        "foundation-topbar": "vendor/foundation/foundation.topbar",
        "foundation-dropdown": "vendor/foundation/foundation.dropdown",
        "foundation-reveal": "vendor/foundation/foundation.reveal",
        "foundation-equalizer": "vendor/foundation/foundation.equalizer",
        "modernizr": "vendor/modernizr/modernizr",
        "mocha": "vendor/mocha/mocha",
        "expect": "vendor/expect/index",
        "sinon": "vendor/sinon/index",
        "es6-promise": "vendor/es6-promise/promise",
        "please": "vendor/pleasejs/Please",
        "tinyscrollbar": "vendor/TinyScrollbar/jquery.tinyscrollbar",
        "testem": "../testem"
    },
    "shim": {
        "backbone": {
            "deps": ["underscore", "jquery"],
            "exports": "Backbone"
        },
        "underscore": {
            "exports": "_"
        },
        "foundation": {
            "deps": ["jquery", "modernizr"],
            "exports": "Foundation"
        },
        "mocha": {
            "deps": ["jquery", "expect"],
            "exports": "mocha"
        },
        "expect": {
            "exports": "expect"
        },
        "sinon": {
            "exports": "sinon"
        },
        "foundation-tooltip": {
            "deps": ["foundation"]
        },
        "foundation-topbar": {
            "deps": ["foundation"]
        },
        "foundation-dropdown": {
            "deps": ["foundation"]
        },
        "foundation-accordion": {
            "deps": ["foundation"]
        },
        "foundation-reveal": {
            "deps": ["foundation"]
        },
        "foundation-equalizer": {
            "deps": ["foundation"]
        }
    },
    "map": {
        "templates": {
            "vendor/underscore": "underscore"
        },
        "*": {
            "jquery": "utils/jquery-private",
            "underscore": "utils/underscore-private",
            "backbone": "utils/backbone-private"
        },
        "utils/jquery-private": {
            "jquery": "jquery"
        },
        "utils/underscore-private": {
            "underscore": "underscore"
        },
        "utils/backbone-private": {
            "backbone": "backbone"
        }
    }
});