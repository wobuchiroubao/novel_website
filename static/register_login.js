'use strict';

function handle_register_login(event, url, form_id, err_id) {
  event.preventDefault();

  let fd = new FormData(document.getElementById(form_id));

  fetch(url, {
    method: 'POST',
    body: fd,
  }).then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error: ${res.status}`);
      }
      return res.json();
    })
    .then(res => {
      console.log(res);
      if (res.err) {
        let err = document.getElementById(err_id);
        err.style.display = 'block';
        err.innerHTML = res.err;
      } else {
        location.href = res.url;
      }
    })
    .catch((err) => console.error(`Failed request: ${err.message}`));
}
