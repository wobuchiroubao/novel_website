'use strict';


function handle_edit_genre(event, new_input_id) {
  if (event.submitter.value != 'edit') { // submit form on save or delete
    return;
  }

  event.preventDefault();
  event.submitter.textContent = 'Save';
  event.submitter.value = 'save';
  let input = document.getElementById(event.target.genre.value);
  let allInputs = document.getElementsByName("genre")
  for (let i = 0; i < allInputs.length; i++) {
    if (allInputs[i] != input) {
      allInputs[i].disabled = true;
    }
  }

  let newInput = document.getElementById(new_input_id);
  let inputLabels = input.labels;
  if (inputLabels.length > 0) {
    inputLabels[0].style.display = 'none';
    newInput.defaultValue = inputLabels[0].textContent;
  }
  input.parentNode.insertBefore(newInput, input.nextSibling);
  newInput.style.display = 'inline';
}
