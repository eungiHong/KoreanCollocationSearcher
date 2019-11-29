var http = require('http');
var url = require('url');
var fs = require('fs');
var events = require('events');
var eventEmitter = new events.EventEmitter();
var connectHandler = function connected() {
  console.log("Connection Succesfull");

  eventEmitter.emit("data_received");
}

eventEmitter.on('connection', connectHandler);

eventEmitter.on('data_received', function() {
  console.log("Data Received");
});

eventEmitter.emit('connection');
console.log("Program has ended");
