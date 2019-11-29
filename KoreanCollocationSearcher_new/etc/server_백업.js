var http = require('http');
var url = require('url');
var fs = require('fs');

var server = http.createServer(function (request, response) {
  fs.readFile('../views/index.html', function(err, data) {
    if (err) {
      response.writeHead(404, {'Content-Type': 'text/html'});
    } else {
      response.writeHead(200, {'Content-Type': 'text/html'});
      response.write(data);
    }
    response.end();
  });
});

server.listen(8080);
