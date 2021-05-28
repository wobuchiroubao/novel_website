'use strict';

function handle_register_login(event, url, form_id, err_id) {
  event.preventDefault();
  let xhr = new XMLHttpRequest();
  let fd = new FormData(document.getElementById(form_id))
  xhr.onreadystatechange = function() {
    if (xhr.readyState != 4) {
      return;
    }
    if (xhr.status != 200) {
      console.log('Failed request:', xhr.status, xhr.statusText);
      return;
    }
    let response = JSON.parse(xhr.responseText);
    if (response.err) {
      let err = document.getElementById(err_id);
      err.style.display = 'block';
      err.innerHTML = response.err;
    } else {
      location.href = response.url;
    }
  };
  xhr.open('POST', url, true);
  xhr.send(fd);
}
