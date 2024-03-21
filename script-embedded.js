const mdn_url = 'https://developer.mozilla.org/en-US/docs/';

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

async function add_compat_data(statuses) {
  const parent = document.querySelector("article.main-page-content");
  let i = 0;
  for await (const table of dynamic_children(parent, '.table-container')) {
    const status = statuses[i++] ?? null;
    update_compat_table(table, status);
    if (statuses.length > 0 && i === statuses.length) {
      break;
    }
  }
}

function replace_child_classes(parent, old_class, new_class) {
  for (const child of parent.querySelectorAll(`.${old_class}`)) {
    child.classList.replace(old_class, new_class);
  }
}

function reassign_compat_table_level(table, old_level, new_level) {
  debugger;
  replace_child_classes(table, `bc-supports-${old_level}`, `bc-supports-${new_level}`);
  replace_child_classes(table, `bc-level-${old_level}`, `bc-level-${new_level}`);
  replace_child_classes(table, `icon-${old_level}`, `icon-${new_level}`);
}

function update_compat_table(table, status) {
  if (status === null) {
    reassign_compat_table_level(table, 'yes', 'partial');
  } else if (status === false) {
    reassign_compat_table_level(table, 'yes', 'no');
    reassign_compat_table_level(table, 'partial', 'no');
  }
}

window.addEventListener('DOMContentLoaded', async _event => {
  if (!location.href.startsWith(mdn_url)) {
    return;
  }

  const path = location.href.slice(mdn_url.length);
  const statuses = overlay[path] ?? [];
  await add_compat_data(statuses);
});

// respond to messages sent from the controlling frame
window.addEventListener('message', event => {

  // user changed the controlling frame's "address bar"
  if (event.data.type === 'nav') {
    window.location.href = event.data.url;
  }
});

const overlay = {"Web/API/Background_Fetch_API":[true,false,null],"Web/API/BackgroundFetchManager":[true],"Web/API/BackgroundFetchRegistration":[false]};
