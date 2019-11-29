const express = require('express');
const router = express.Router();
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const corpusType = "Sejong";

// 연어 테이블에서 예문 띄워주는 경우
router.get('/single_result', function(req, res, next) {
  var pair = req.query.pair;
  var index = req.query.index;

  examplePath = path.join("./data/" + corpusType + "/examples", pair.split("/")[1], pair.split("/")[0], index + ".txt");
  console.log("path: " + examplePath);
  var examples = fs.readFileSync(examplePath, 'utf-8').split('\n');
  examples.pop(); //마지막에 공백 제거
  res.json(examples);
});

// 중복 단어(ex: 차다)에서 품사별로 연어 목록 띄워주는 경우
router.get('/plural_results', function(req, res, next) {

  var pair = req.query.pair;
  var morpheme = pair.split("/")[0];
  var tag = pair.split("/")[1];
  var filePath = path.join("./data/" + corpusType + "/collocations", tag, morpheme + ".txt");
  var lines = fs.readFileSync(filePath, 'utf-8').split('\n');
  lines.pop(); // 마지막에 공백 제거

  var collocations = []
  for (let i = 0; i < lines.length; i++) {
    var split_line = lines[i].split('\t');
    collocations.push( { collocation: split_line[0], frequency: split_line[1] } );
  }
  res.json(collocations);
});

/* POST */
// form을 통해 전달 받은 검색어 처리
router.post('/', function(req, res, next) {

  var query = req.body.user_query;
  var dataPath = "./data/" + corpusType + "/collocations";
  var matchedItem = [];

  // 폴더를 순회하면서 검색어와 매칭되는 파일 있는지 확인
  var directories = fs.readdirSync(dataPath);
  directories.forEach(function(directory) {
    dirPath = path.join(dataPath, directory)
    var files = fs.readdirSync(dirPath);
    files.forEach(function(file) {
      if (query == path.parse(file).name) {
        matchedItem.push(path.join(dirPath, file));
        //console.log("file name: " + path.join(dirPath, file));
      }
    });
  });

  // 매치되는 파일이 없는 경우, flag == 0
  if (matchedItem.length == 0) {
    res.render('action_page.html', { colData: 0, pair: 0, flag: 0 });
  }
  // 매치되는 파일이 1개인 경우, (1) 연어 array 및 추후 example 전시를 위한 (2) 형태소/품사 string, (3) flag == 1 리턴
  else if (matchedItem.length == 1) {
    var lines = fs.readFileSync(matchedItem[0], 'utf-8').split('\n');
    lines.pop(); //마지막에 공백 제거
    var collocations = []
    for (let i = 0; i < lines.length; i++) {
      var split_line = lines[i].split('\t');
      collocations.push( { collocation: split_line[0], frequency: split_line[1] } );
    }
    morpheme_and_tag = spliter(matchedItem[0]);
    res.render('action_page.html', { colData: JSON.stringify(collocations), pair: JSON.stringify(morpheme_and_tag), flag: 1 });
  }
  // 매치되는 파일이 2개인 경우, (1) '형태소/품사' string을 원소로 갖는 array 리턴 (pair)
  else if (matchedItem.length > 1) {
    for (let i = 0; i < matchedItem.length; i++) {
      // matchedItem[i] = "data\\collocations\\동사\\차다.txt"
      //console.log(matchedItem[i]);
      morpheme_and_tag = spliter(matchedItem[i]);
      matchedItem[i] = morpheme_and_tag;
    }
    res.render('action_page.html', { colData: 0, pair: JSON.stringify(matchedItem), flag: 2 });
  }

});

module.exports = router;

// 경로(예: "data\\Sejong\\collocations\\동사\\차다.txt")를 받아서 "형태소/품사" 쌍 반환
function spliter(filePath) {
  splitStr = filePath.split("\\");
  morpheme_and_tag = path.parse(splitStr[4]).name + "/" + splitStr[3];
  return morpheme_and_tag;
}
