function numbersSubmit() {

var href = window.location.pathname;
var numbers = document.forms[0].elements["myInputs[]"];
var numbers_array = [];
if (numbers.length == null || numbers.length == 0) {
    numbers_array[0] = document.getElementById("input-number").value;
}
for (var i = 0; i < numbers.length; i++) {
    numbers_array[i] = numbers[i].value;
}
var myJSON = JSON.stringify(numbers_array);
var request = new XMLHttpRequest();
request.open('POST', "/api/surveys/" + href.match(/([^\/]*)\/*$/)[1] + "/phoneNumbers");
request.setRequestHeader('Content-Type', 'application/json');
request.send(myJSON);
};