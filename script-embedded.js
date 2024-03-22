const overlay = {"Web/API/WebSocket":[[1,1]],"Web/API/WebSocket/WebSocket":[[1]],"Web/API/WebSockets_API":[[1,1]]};
const mdn_url = 'https://developer.mozilla.org/en-US/docs/';

const UNKNOWN = 0;
const TESTED = 1;
const EXPECTED = 2;
const PARTIAL = 3;
const TODO = 4;
const NEVER = 5;

window.addEventListener('DOMContentLoaded', async _event => {
  if (!location.href.startsWith(mdn_url)) {
    return;
  }

  const path = location.href.slice(mdn_url.length);
  const support_tables = overlay[path] ?? [];
  await add_compat_data(support_tables);
});

async function add_compat_data(support_specs) {
  const parent = document.querySelector("article.main-page-content");

  let i = 0;
  for await (const table of dynamic_children(parent, '.table-container')) {
    const tbody = table.querySelector('tbody');
    const support_spec = support_specs[i++] ?? UNKNOWN;
    update_compat_table(tbody, support_spec);
  }
}

function update_compat_table(tbody, support_spec) {
  return (
    Array.isArray(support_spec) ?
    update_compat_rows(tbody, support_spec) :
    update_compat_context(tbody, support_spec)
  );
}

function update_compat_rows(tbody, support_rows) {
    let i = 0;
    for (const row of tbody.querySelectorAll('tr')) {
      const support_row = support_rows[i++] ?? UNKNOWN;
      update_compat_context(row, support_row);
    }
}

function update_compat_context(element, support) {
  switch (support) {

    case UNKNOWN:
    case PARTIAL:
    case EXPECTED:
      reassign_compat_table_level(element, 'yes', 'partial');
      break;

    case TODO:
    case NEVER:
      reassign_compat_table_level(element, 'yes', 'no');
      reassign_compat_table_level(element, 'partial', 'no');
      break;
  }
}

function reassign_compat_table_level(element, old_level, new_level) {
  replace_child_classes(element, `bc-supports-${old_level}`, `bc-supports-${new_level}`);
  replace_child_classes(element, `bc-level-${old_level}`, `bc-level-${new_level}`);
  replace_child_classes(element, `icon-${old_level}`, `icon-${new_level}`);
}

function replace_child_classes(parent, old_class, new_class) {
  for (const child of parent.querySelectorAll(`.${old_class}`)) {
    child.classList.replace(old_class, new_class);
  }
}

// respond to messages sent from the controlling frame
window.addEventListener('message', event => {

  // user changed the controlling frame's "address bar"
  if (event.data.type === 'nav') {
    window.location.href = event.data.url;
  }
});

function dynamic_children(target, child_selector) {
  const options = { childList: true, subtree: false };
	return {
		async * [Symbol.asyncIterator]() {
			for await (const mutations of batchedDomMutations(target, options)) {
        for (const mutation of mutations) {
          for (const child of mutation.addedNodes) {
            if (child.matches(child_selector)) {
              yield child;
            }
          }
        }
			}
		},
	};
}

// https://github.com/sindresorhus/dom-mutations
function batchedDomMutations(target, {signal, ...options} = {}) {
	return {
		async * [Symbol.asyncIterator]() {
			signal?.throwIfAborted();

			let resolveMutations;
			let rejectMutations;

			const observer = new MutationObserver(mutations => {
				resolveMutations?.(mutations);
			});

			observer.observe(target, options);

			signal?.addEventListener('abort', () => {
				rejectMutations?.(signal.reason);
				observer.disconnect();
			}, {once: true});

			try {
				while (true) {
					signal?.throwIfAborted();

					yield await new Promise((resolve, reject) => {
						resolveMutations = resolve;
						rejectMutations = reject;
					});
				}
			} finally {
				observer.disconnect();
			}
		},
	};
}
