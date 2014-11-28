var http = require("http");
var fs = require("fs");
var md5 = require("MD5");

var server = http.createServer(function(req, resp){
	var useragent = req.headers["user-agent"];
	var filename = "coverage_"+md5(useragent)+".json";
	if(useragent.indexOf("Phantom") === -1) {
		console.log("Saving Code Coverage data to browser "+useragent);
		req.pipe(fs.createWriteStream(filename));
	}
	else {
		console.log("Ignoring code coverage data to browser "+useragent);
		req.pipe(fs.createWriteStream("/tmp/"+filename));
	}
	req.on("end", function(){
		resp.end();
	});
});

var port = 7358;
server.listen(port);
console.log("Coverage server listening on", port);
