'use strict';


function replace_block(hide_id, show_id) {
  document.getElementById(hide_id).style.display = 'none';
  document.getElementById(show_id).style.display = 'block';
}


function send_text(url, text) {
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'text/plain',
    },
    body: text.toString(),
  }).then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error: ${res.status}`);
      }
      location.href = url;
    })
    .catch((err) => console.error(`Failed request: ${err.message}`));
}


function redirect(url) {
  location.href = url;
}
