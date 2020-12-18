var http = require("http");
var static = require("node-static");
var file = new static.Server();

http.createServer (function (request, response) {
file.serve (request, response);
response.writeHead(200, {"Content-Type": "text/plain"});
response.end("Hello Node!");
}).listen(1337, "127.0.0.1");
console.log("Server running at http://127.0.0.1:1337/");