var counter = 1;
function addInput(divName, entry_type){
     var newdiv = document.createElement('div');
     newdiv.innerHTML = entry_type + " " + (counter + 1) + " <br><input type='text' name='myInputs[]'>";
     document.getElementById(divName).appendChild(newdiv);
     counter++;
}