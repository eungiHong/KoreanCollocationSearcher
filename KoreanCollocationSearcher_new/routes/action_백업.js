const express = require('express');
const router = express.Router();
const bodyParser = require('body-parser');
const fs = require('fs');
const readline = require('readline');
const async = require('async');

/* GET */
/*
router.get('/', function(req, res, next) {
    var id = req.query.id;
    var age = req.query.age;
    console.log("## get request");
    res.render('result_page.html', { title: 'Express', id: id, age: age, method: "get" });
});*/

/* POST */
router.post('/', function(req, res, next) {

  var query = req.body.user_query;
  var tasks = [
    function (callback) {

      var col = [];
      var readInterface = readline.createInterface({
          input: fs.createReadStream("./data/동사/" + query + ".txt")
          //output: process.stdout,
      });
      readInterface.on('line', function(line) {
        col.push(line);
        console.log("length: " + col.length);
      }).on('close', function() {
        readInterface.close();
      });
      callback(null, col);
    },

    function (data, callback) {
      console.log("second length: " + data);
      res.render('action_page.html', {
        cols: data,
        method: "post" });

      callback(null);
    }
  ];

  async.waterfall(tasks, function (err) {
    if (err) console.log('err');
    else console.log('done');
  })


});

/*
var readInterface = readline.createInterface({
    input: fs.createReadStream("./data/동사/" + query + ".txt")
    //output: process.stdout,
});
readInterface.on('line', function(line) {
  data.push(line);
  console.log("length: " + data.length);
}).on('close', function() {
  readInterface.close();
});
*/

/*
function sendData(data) {

  console.log("second length: " + data.length);
  console.log("## post request");
  res.render('action_page.html', {
    query: query,
    cols: collocations,
    method: "post" });
}
*/

module.exports = router;
