// Will load config before loading bootstrapper and all the other modules..
require(["config"], function(){
    "use strict";
	return require(["bootstraper"]);
});