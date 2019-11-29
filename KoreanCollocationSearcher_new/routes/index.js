var express = require('express');
var router = express.Router();
var bodyParser = require('body-parser');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index.html');
});

router.get('/index', function(req, res, next) {
  res.render('index.html');
});

router.get('/about', function(req, res, next) {
  res.render('about.html');
});

module.exports = router; // router를 export한다는 의미
