// Will load config before loading bootstrapper and all the other modules..
require(["config"], function(){
	return require(["bootstraper"]);
});