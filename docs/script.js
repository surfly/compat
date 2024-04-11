let session_created = false;

document.addEventListener('DOMContentLoaded', (event) => {
  const input_api_key = document.querySelector('#api_key');

  const params = new URLSearchParams(document.location.search);
  const api_key = params.get("api_key");
  if (api_key !== null) {
    input_api_key.value = api_key;
  }

  // wire up links to navigate within session
  for (const a of document.querySelectorAll('a.navigate')) {
    a.addEventListener('click', click_example_link);
  }

  // wire up form submit on controls to start the session or send a navigation command
  document.querySelector('form').addEventListener('submit', handle_submit);
});

// request a new session from the Surfly API, returns URL for iframe.src
async function create_session() {
  const api_key = document.querySelector('#api_key').value;
  const url = document.querySelector('#url').value;
  const server = document.querySelector('#server').value;

  if (!api_key || !url) return;

  const params = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url,
      headless: true,
      script_embedded: `https://raw.githubusercontent.com/surfly/compat/main/docs/script-embedded.js`,
    }),
  };

  const res = await fetch(`https://${server}/v2/sessions/?api_key=${api_key}`, params);
  const data = await res.json();
  return data.headless_link;
}

// load the session link in the iframe and swap to in-session UI
function show_session(headless_link) {
  for (const node of document.querySelectorAll('.hide-after-start')) {
    node.setAttribute('hidden', '');
  }
  for (const node of document.querySelectorAll('.show-after-start')) {
    node.removeAttribute('hidden');
  }
  document.querySelector('iframe').src = headless_link;
}

async function handle_submit(event) {
  event.preventDefault();
  if (session_created) {
    navigate();
  } else {
    const url = await create_session();
    session_created = true;
    show_session(url);
  }
}

function click_example_link(event) {
  event.preventDefault();
  const url = event.target.href;
  document.querySelector('#url').value = url;
  navigate();
}

// send a command to the script_embedded running inside the session
function command(data) {
  document.querySelector('iframe').contentWindow.postMessage(data, '*');
}

// tell the script_embedded to load a provided URL
function navigate() {
  const url = document.querySelector('#url').value;
  command({type: 'nav', url});
}

console.log(location.origin)
