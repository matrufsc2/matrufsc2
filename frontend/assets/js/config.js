require.config({
	"baseUrl": "/js/",
	"paths" : {
		"jquery"       : "vendor/jquery/jquery",
		"underscore"   : "vendor/underscore/underscore",
		"backbone"     : "vendor/backbone/backbone",
		"chaplin"      : "vendor/chaplin/chaplin",
		"tv4"          : "vendor/tv4/tv4",
		"es5-shim"     : "vendor/es5-shim/es5-shim",
		"moment"       : "vendor/moment/moment",
		"foundation"   : "vendor/foundation/foundation",
		"modernizr"    : "vendor/modernizr/modernizr",
		"mocha"        : "vendor/mocha/mocha",
		"expect"       : "vendor/expect/index",
		"query-engine" : "vendor/query-engine/index",
		"sinon"        : "vendor/sinon/index",
		"bluebird"     : "vendor/bluebird/bluebird",
		"select2"	   : "vendor/select2/select2",
		"please"       : "vendor/pleasejs/Please",
		"diacritic"    : "vendor/diacritic/diacritics",
		"testem"       : "../testem"
	},
	"shim" : {
		"query-engine": {
			"deps"    : ["backbone"],
			"exports" : "QueryEngine"
		},
		"backbone": {
			"deps"    : ["underscore", "jquery"],
			"exports" : "Backbone"
		},
		"underscore": {
			"exports" : "_"
		},
		"tv4": {
			"exports" : "tv4"
		},
		"foundation": {
			"deps"    : ["jquery", "modernizr"],
			"exports" : "$"
		},
		"mocha" : {
			"deps"    : ["jquery", "expect"],
			"exports" : "mocha"
		},
		"expect" : {
			"exports" : "expect"
		},
		"sinon"  : {
			"exports": "sinon"
		}
	},
	"map" : {
		"templates" : {
			"vendor/underscore" : "underscore"
		}
	}
});