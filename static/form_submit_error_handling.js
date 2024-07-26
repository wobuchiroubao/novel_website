'use strict';


function handle_form_submit_errors(event, url, err_id) {
  event.preventDefault();

  let fd = new FormData(event.target);

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
        console.log(res.url);
        location.href = res.url;
      }
    })
    .catch((err) => console.error(`Failed request: ${err.message}`));
}
