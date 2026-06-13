import { el, debounce } from '../utils.js';
import { navigate } from '../router.js';
import { getInstalledApps, launchApp, uninstallApp, createConfig, updateLaunchType, openExternal, checkForUpdates } from '../api.js';
import { showToast } from '../components/toasts.js';
import { renderEmptyState } from '../components/emptystate.js';
import { refreshStatusBar } from '../components/statusbar.js';

let allApps = [];

export function renderLibrary(container) {
    container.innerHTML = '';

    const header = el('div', { className: 'view-header' }, [
        el('h1', { className: 'view-title', text: 'Your Library' }),
        el('p', { className: 'view-subtitle', text: 'Manage your installed applications' })
    ]);

    // Search bar
    const searchInput = el('input', {
        className: 'library-search',
        type: 'text',
        placeholder: 'Search installed apps...'
    });

    const actionsBar = el('div', { className: 'library-actions' }, [
        searchInput,
        el('button', {
            className: 'btn btn-secondary btn-sm',
            text: 'Check Updates',
            onClick: async (e) => {
                e.target.disabled = true;
                e.target.textContent = 'Checking...';
                const updates = await checkForUpdates();
                if (updates && updates.length > 0) {
                    showToast(`${updates.length} update(s) available`, 'info');
                } else {
                    showToast('All apps up to date', 'success');
                }
                e.target.disabled = false;
                e.target.textContent = 'Check Updates';
            }
        })
    ]);

    const listContainer = el('div', { className: 'library-list', id: 'library-list' });
    listContainer.appendChild(el('div', { className: 'detail-loading' }, [
        el('div', { className: 'spinner' }),
        el('span', { text: 'Loading apps...' })
    ]));

    container.appendChild(header);
    container.appendChild(actionsBar);
    container.appendChild(listContainer);

    // Search handler
    const doSearch = debounce((query) => {
        const q = query.toLowerCase();
        const filtered = allApps.filter(a =>
            a.name.toLowerCase().includes(q) ||
            (a.description && a.description.toLowerCase().includes(q))
        );
        renderAppList(listContainer, filtered);
    }, 200);

    searchInput.addEventListener('input', (e) => doSearch(e.target.value));

    loadApps(listContainer);
}

async function loadApps(container) {
    allApps = await getInstalledApps();
    renderAppList(container, allApps);
    refreshStatusBar();
}

function renderAppList(container, apps) {
    container.innerHTML = '';

    if (!apps || apps.length === 0) {
        renderEmptyState(container, {
            type: 'library',
            title: 'No apps installed',
            description: 'Paste a GitHub URL on the Home screen to install your first app',
            action: { label: 'Go to Home', handler: () => navigate('/') }
        });
        return;
    }

    const list = el('div', { className: 'library-items' },
        apps.map(app => createAppRow(app))
    );
    container.appendChild(list);
}

function createAppRow(app) {
    const launchType = app.launch_type || 'auto';
    const typeLabel = launchType === 'cli' ? 'CLI' : launchType === 'gui' ? 'GUI' : 'Auto';

    const row = el('div', { className: 'library-row' }, [
        el('div', { className: 'library-row-icon', text: app.name.charAt(0).toUpperCase() }),
        el('div', { className: 'library-row-info' }, [
            el('h3', { className: 'library-row-name', text: app.name }),
            el('div', { className: 'library-row-meta' }, [
                el('span', { className: 'library-row-version', text: app.entry_point || 'main.py' }),
                el('span', { className: `library-row-status status-launch-${launchType}`, text: typeLabel })
            ])
        ]),
        el('div', { className: 'library-row-actions' }, [
            el('button', {
                className: 'btn btn-green btn-sm',
                text: 'Launch',
                onClick: async () => {
                    const result = await launchApp(app.dir_name);
                    if (result.success) {
                        showToast(`Launched ${app.name}`, 'success');
                    } else {
                        showToast('Launch failed: ' + result.error, 'error');
                    }
                }
            }),
            el('button', {
                className: 'btn btn-secondary btn-sm',
                text: typeLabel,
                title: 'Click to toggle: Auto → GUI → CLI',
                onClick: async () => {
                    const next = launchType === 'auto' ? 'gui' : launchType === 'gui' ? 'cli' : 'auto';
                    await updateLaunchType(app.dir_name, next);
                    showToast(`Launch type set to ${next}`, 'success');
                    const listContainer = document.getElementById('library-list');
                    if (listContainer) loadApps(listContainer);
                }
            }),
            el('button', {
                className: 'btn btn-secondary btn-sm',
                text: 'Config',
                onClick: async () => {
                    const result = await createConfig(app.dir_name);
                    if (result.success) {
                        showToast('Config updated', 'success');
                    } else {
                        showToast('Config error: ' + result.error, 'error');
                    }
                }
            }),
            el('button', {
                className: 'btn btn-secondary btn-sm',
                text: 'GitHub',
                onClick: () => openExternal(app.url)
            }),
            el('button', {
                className: 'btn btn-danger btn-sm',
                text: 'Uninstall',
                onClick: async () => {
                    if (confirm(`Uninstall ${app.name}?`)) {
                        const result = await uninstallApp(app.dir_name);
                        if (result.success) {
                            showToast(`${app.name} uninstalled`, 'success');
                            const listContainer = document.getElementById('library-list');
                            if (listContainer) loadApps(listContainer);
                        } else {
                            showToast('Uninstall failed: ' + result.error, 'error');
                        }
                    }
                }
            })
        ])
    ]);

    return row;
}
