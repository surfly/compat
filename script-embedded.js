const bcd_url_prefix = 'https://bcd.developer.mozilla.org/bcd/api/v0/current/';
const scd_url_prefix = 'https://raw.githubusercontent.com/qguv/surfly-compat-data/data/scd/';

// intercept requests to MDN browser-compat-data
window.__native_fetch = window.fetch;
window.fetch = function(url, ...rest) {
  if (url.startsWith(bcd_url_prefix)) {
    url = url.replace(bcd_url_prefix, scd_url_prefix);
  }
  return window.__native_fetch.call(this, url, ...rest);
};

// respond to messages sent from the controlling frame
window.addEventListener('message', event => {

  // user changed the controlling frame's "address bar"
  if (event.data.type === 'nav') {
    window.location.href = event.data.url;
  }
});

// wider tables
const override_style = document.createElement('style');
override_style.innerHTML = '.main-wrapper { max-width:2000px !important; }';
document.head.append(override_style);
