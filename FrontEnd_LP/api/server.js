const express = require('express');
const detections = require('./models/detections');
const app = express();
const Detections = require("./models/detections") 
User = require('./sequelize')

const API_PORT = process.env.API_PORT || 8080;
app.use(express.static("public"));

app.listen(API_PORT, () => console.log(`A ouvir na porta ${API_PORT}`));

require('./routes/resultados')(app);

module.exports = app;

// Import necessary modules for the project
// A basic http server that we'll access to view the stream
const http = require('http');
// To keep things simple we read the index.html page and send it to the client
const fs = require('fs');
// WebSocket for broadcasting stream to connected clients
const WebSocket = require('ws');
// We'll spawn ffmpeg as a separate process
const spawn = require('child_process').spawn;
// For sending SDK commands to Tello
const dgram = require('dgram');

// HTTP and streaming ports
const HTTP_PORT = 3000;
const STREAM_PORT = 3001

// Tello's ID and Port
const TELLO_IP = '192.168.10.1'
const TELLO_PORT = 8889

//Create the web server
server = http.createServer(function(request, response) {

  // Read file from the local directory and serve to user
  fs.readFile(__dirname + '/api/public/' + request.url, function (err,data) {
    if (err) {
      response.writeHead(404);
      response.end(JSON.stringify(err));
      return;
    }
    response.writeHead(200);
    response.end(data);
  });

}).listen(HTTP_PORT); // Listen on port 3000

//Create the stream server where the video stream will be sent
const streamServer = http.createServer(function(request, response) {

  // When data comes from the stream (FFmpeg) we'll pass this to the web socket
  request.on('data', function(data) {
    // Now that we have data let's pass it to the web socket server
    webSocketServer.broadcast(data);
  });

}).listen(STREAM_PORT); // Listen for streams on port 3001

//Begin web socket server
const webSocketServer = new WebSocket.Server({
  server: streamServer
});

// Broadcast the stream via websocket to connected clients
webSocketServer.broadcast = function(data) {
  webSocketServer.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(data);
    }
  });
};


// Delay for 1 seconds before we start ffmpeg
setTimeout(function() {
  var args = [
    "-i", "udp://0.0.0.0:11111",
    "-r", "30",
    "-s", "960x720",
    "-codec:v", "mpeg1video",
    "-b", "800k",
    "-f", "mpegts",
    "http://127.0.0.1:3001/stream"
  ];

  // Spawn an ffmpeg instance
  var streamer = spawn('ffmpeg', args);
  // Uncomment if you want to see ffmpeg stream info
  //streamer.stderr.pipe(process.stderr);
  streamer.on("exit", function(code){
      console.log("Failure", code);
  });
}, 500);