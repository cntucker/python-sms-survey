function questionSubmit() {
var href = window.location.pathname;
var questionText = document.getElementById("question-text").value;
var index = document.getElementById("index").value ;
var myObj = [{ "questionText":questionText, "questionIndex":index}];
var myJSON = JSON.stringify(myObj);
var request = new XMLHttpRequest();
request.open('POST', "/api/surveys/" + href.match(/([^\/]*)\/*$/)[1] + "/questions");
request.setRequestHeader('Content-Type', 'application/json');
request.send(myJSON);
};