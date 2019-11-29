// 라이브러리 설정
const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const bodyParser = require('body-parser');

// index.js, action.js에서 module.export = router; 코드를 통해 export한 것을 import
const indexRouter = require('./routes/index');
const actionRouter = require('./routes/action');

const port = 8080;
const hostname = '192.168.0.18';
const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.engine('html', require('ejs').renderFile);

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(bodyParser.urlencoded({ extended: false}));
app.use(cookieParser());
// public 자원(css, image) 사용하도록 설정
app.use(express.static(path.join(__dirname, 'public')));

// 라우터 설정
app.use('/', indexRouter);
app.use('/action', actionRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error.html');
});

// 현재 app.js를 import하는 코드는 없으므로 주석 처리
//module.exports = app;

const server = app.listen(port, function() {
  console.log("Express server has started on port " + port);

});
