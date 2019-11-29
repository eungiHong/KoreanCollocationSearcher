// 매치되는 파일이 없는 경우, flag == 0
if (flag == 0) {
  let p = "검색 결과가 없습니다";
  document.getElementById("no_result").innerHTML = p;
}
// 매치되는 파일이 1개인 경우, (1) 연어 array 및 추후 example 전시를 위한 (2) 형태소/품사 string, (3) flag == 1 리턴
else if (flag == 1) {
  let table="<tr><th class='first_column'>번호</th><th class='second_column'>연어</th><th class='third_column'>빈도수</th></tr>";
  console.log(colArray);
  for (let i = 0; i < colArray.length; i++) {
    if (i == 50) break;
    table += "<tr><td class='first_column'>" + (i + 1) + "</td>"
    + "<td class='second_column'><p onclick='loadExamples(\"" + pair + "\", \"" + (i + 1) +  "\")'>" + colArray[i].collocation + "</p><ul id='id" + (i + 1) + "\'></ul></td>"
    + "<td class='third_column'>" + colArray[i].frequency + "</td></tr>";
  }
  //console.log("tabel: " + table);
  document.getElementById("results").innerHTML = table;
  document.getElementById("results").className = "col_table";
}
// 매치되는 파일이 2개인 경우, (1) '형태소/품사' string을 원소로 갖는 array 리턴 (pair)
else if (flag == 2) {
  let table="<tr><th>두 가지 이상의 단어가 검색되었습니다.</th></tr>";
  console.log(pair);
  for (let i = 0; i < pair.length; i++) {
    table += "<tr><td><p onclick='loadFile(\"" + pair[i] +  "\")'>" + pair[i] + "</p></td></tr>";
  }
  document.getElementById("results").innerHTML = table;
  document.getElementById("results").className = "custom_table";
}

// 서버에 예문 요청
function loadExamples(pair, index) {
  console.log("loadExample called");
  console.log("pair: " + pair);
  console.log("action?pair=" + pair + ", index=" + index);
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    // this: XHMLHttpRequest
    if (this.readyState == 4 && this.status == 200) {
      displayExamples(this, index);
    }
  };
  xhttp.open("GET", "action/single_result?pair=" + pair + "&index=" + index, true);
  xhttp.send();
}

// 예문 전시
function displayExamples(xmlHttpRequest, index) {
  let examples = JSON.parse(xmlHttpRequest.response);
  let list = "<ul class='w3-ul w3-border'>";
  for (let i = 0; i < examples.length; i++) {
    if (i == 50) break;
    list += "<li>" + examples[i] + "</li>"
  }
  list += "</ul>";
  // console.log("old html: " + document.getElementById("id" + index).innerHTML.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\"/g, "\'"));
  // console.log("new html: " + list);
  if ( document.getElementById("id" + index).innerHTML.length > 0) {
    document.getElementById("id" + index).innerHTML = null;
  }
  else {
    document.getElementById("id" + index).innerHTML = list;
  }
}

// 중복 결과(예: 차다)일 때, 각 품사별로 연어 목록 표시
function loadFile(pair) {
  console.log("loadFile called");
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    // this: XHMLHttpRequest
    if (this.readyState == 4 && this.status == 200) {
      displayFile(this, pair);
    }
  };
  xhttp.open("GET", "action/plural_results?pair=" + pair, true);
  xhttp.send();
}

// 중복 결과(예: 차다)일 때, 연어 목록 전시하는 경우에만 해당
function displayFile(xmlHttpRequest, pair) {
  // JSON into Array
  let colArray = JSON.parse(xmlHttpRequest.response);
  let table="<tr><th class='first_column'>번호</th><th class='second_column'>연어</th><th class='third_column'>빈도수</th></tr>";
  let len = colArray[0].length;
  for (let i = 0; i < colArray.length; i++) {
    if (i == 50) break;
    table += "<tr><td class='first_column'>" + (i + 1) + "</td>"
    + "<td class='second_column'><p onclick='loadExamples(\"" + pair + "\", \"" + (i + 1) +  "\")'>" + colArray[i].collocation + "</p><ul id='id" + (i + 1) + "\'></ul></td>"
    + "<td class='third_column'>" + colArray[i].frequency + "</td></tr>";
  }
  document.getElementById("additional").innerHTML = table;
  document.getElementById("additional").className = "col_table";
}
