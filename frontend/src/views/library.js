import { el, debounce } from '../utils.js';
import { navigate } from '../router.js';
import { getInstalledApps, launchApp, uninstallApp, createConfig, updateLaunchType, openExternal, checkForUpdates, repairApp, getAvatarUrl, getAppSize, updateApp } from '../api.js';
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

    container.appendChild(el('button', {
        className: 'library-fab',
        html: '💬 Doesn\'t work? <strong>Open an issue</strong>',
        onClick: () => openExternal('https://github.com/korrykatti/thunder/issues/new')
    }));

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
    const avatarUrl = getAvatarUrl(app.url || '');
    const launchCount = app.launch_count || 0;
    const lastLaunched = app.last_launched ? formatRelativeTime(app.last_launched) : null;

    const avatarImg = avatarUrl
        ? el('img', {
            className: 'library-row-avatar',
            src: avatarUrl,
            alt: app.name,
            onerror: function() { this.style.display = 'none'; this.nextSibling.style.display = 'flex'; }
        })
        : null;
    const avatarFallback = el('div', {
        className: 'library-row-icon',
        text: app.name.charAt(0).toUpperCase(),
        style: avatarUrl ? { display: 'none' } : {}
    });

    const metaChildren = [
        el('span', { className: 'library-row-version', text: app.entry_point || 'main.py' }),
        el('span', { className: `library-row-status status-launch-${launchType}`, text: typeLabel })
    ];

    if (launchCount > 0) {
        metaChildren.push(el('span', { className: 'library-row-usage', text: `${launchCount} launch${launchCount !== 1 ? 'es' : ''}` }));
    }
    if (lastLaunched) {
        metaChildren.push(el('span', { className: 'library-row-lastused', text: lastLaunched }));
    }

    const row = el('div', { className: 'library-row' }, [
        ...([avatarImg, avatarFallback].filter(Boolean)),
        el('div', { className: 'library-row-info' }, [
            el('h3', { className: 'library-row-name', text: app.name }),
            el('div', { className: 'library-row-meta' }, metaChildren)
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
                title: 'Click to toggle: Auto \u2192 GUI \u2192 CLI',
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
                text: 'Update',
                title: 'Download latest version from GitHub',
                onClick: async (e) => {
                    e.target.disabled = true;
                    e.target.textContent = 'Updating...';
                    const result = await updateApp(app.dir_name);
                    if (result.success) {
                        showToast(`${app.name} updated`, 'success');
                    } else {
                        showToast('Update failed: ' + result.error, 'error');
                    }
                    e.target.disabled = false;
                    e.target.textContent = 'Update';
                }
            }),
            el('button', {
                className: 'btn btn-secondary btn-sm',
                text: 'Repair',
                title: 'Recreate venv and reinstall dependencies',
                onClick: async (e) => {
                    e.target.disabled = true;
                    e.target.textContent = 'Repairing...';
                    const result = await repairApp(app.dir_name);
                    if (result.success) {
                        showToast(`${app.name} repaired`, 'success');
                    } else {
                        showToast('Repair failed: ' + result.error, 'error');
                    }
                    e.target.disabled = false;
                    e.target.textContent = 'Repair';
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
                    const size = await getAppSize(app.dir_name);
                    const msg = `Uninstall ${app.name}?\n\nThis will delete:\n\u2022 App files (${size})\n\u2022 Virtual environment\n\u2022 Configuration`;
                    if (confirm(msg)) {
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

function formatRelativeTime(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now - d;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString();
}
