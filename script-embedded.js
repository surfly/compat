const bcd_url_prefix = 'https://bcd.developer.mozilla.org/bcd/api/v0/current/';
const scd_url_prefix = 'https://cdn.jsdelivr.net/gh/qguv/surfly-compat-data@data/scd/';

const UNKNOWN = 0;
const TESTED = 1;
const EXPECTED = 2;
const PARTIAL = 3;
const TODO = 4;
const NEVER = 5;

window.__native_fetch = window.fetch;
window.fetch = function(url, ...rest) {
  if (url.startsWith(bcd_url_prefix)) {
    url = url.replace(bcd_url_prefix, scd_url_prefix);
  }
  return window.__native_fetch.call(this, url, ...rest);
};
