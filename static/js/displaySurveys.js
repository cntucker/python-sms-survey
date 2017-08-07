var req = new XMLHttpRequest();
var table = document.getElementById("survey-table");
req.open('GET', '/api/surveys');
req.onload = function() {
    var data = JSON.parse(req.responseText);
    data = data.surveys;
    addHTMLTable(data);
};
req.send();

function addHTMLTable(data){
    var htmlString = "";
    for(i = 0; i < data.length; i++) {
        htmlString += '<tr><td>' + '<a href="/addQuestions/' + data[i].surveyId
        + '">View/Add Questions</a><br/><a href="/addNumbers/' + data[i].surveyId
        + '">Send Survey</a></td><td>'+ data[i].surveyId + '</td><td>' + data[i].surveyName
        + '</td><td>' + data[i].surveyNumber + '</td></tr>';
    }
    table.insertAdjacentHTML('beforeend', htmlString);
}
