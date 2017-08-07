var req = new XMLHttpRequest();
var href = location.href;
var table = document.getElementById("question-table");
var info = document.getElementById("survey-info");
var responses = document.getElementById("tab2");
var url = '/api/survey/' + href.match(/([^\/]*)\/*$/)[1];
req.open('GET', url);
req.onload = function() {
    var data = JSON.parse(req.responseText);
    if(data.surveyId == null) {
        return;
    }
    addHTMLText(data);
    addHTMLTable(data);
    addResponseTables(data);
};
req.send();

function addHTMLTable(data){
    var htmlString = "";
    data = data.questions
    for(i = 0; i < data.length; i++) {
        htmlString += '<tr class="details"><td>' + data[i].questionId + '</td><td>' + data[i].questionText + '</td><td>' + data[i].questionIndex + '</td>';
        htmlString += '</tr>';
        addResponseTables(data[i]);
    }
    table.insertAdjacentHTML('beforeend', htmlString);
}

function addHTMLText(data){
    info.insertAdjacentHTML('beforeend', '<h5>Survey ID: ' + data.surveyId + '</h5>');
    info.insertAdjacentHTML('beforeend', '<h5>Survey Name: ' + data.surveyName + '</h5>');
}

function addHTMLAnswers(data) {
    var htmlAnswersString = '<tr class="details"><td colspan="3"><div class="slide"><p>';
    htmlAnswersString += data;
    htmlAnswersString += '</p></div></td></tr>';
    return htmlAnswersString;
}


function addResponseTables(data2) {
    htmlResponseString = "<p>Question Text: " + data2.questionText + "</p>";
    htmlResponseString += '<table class="small"><tr><th>Answer Id</th><th>Phone Number</th><th>Answer Text</th><th>Timestamp</th></tr>';
    if(data2.answers == null) {
        return;
    }
    for(j = 0; j < data2.answers.length; j++) {
        htmlResponseString += '<tr><td>' + data2.answers[j].answerId + '</td><td>' + data2.answers[j].phoneNumber + '</td><td>' + data2.answers[j].answerText + '</td><td>' + data2.answers[j].timestamp + '</td></tr>';
    }

    htmlResponseString += "</table></br>";

    responses.insertAdjacentHTML('beforeend', htmlResponseString);
}
