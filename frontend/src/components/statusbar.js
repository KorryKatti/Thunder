import { el } from '../utils.js';
import { getInstalledApps, getUpdateCount } from '../api.js';

export function renderStatusBar(container) {
    const bar = el('div', { className: 'statusbar' }, [
        el('div', { className: 'statusbar-left' }, [
            el('span', { className: 'statusbar-brand', html: '⚡ <strong>Thunder</strong>' }),
            el('span', { className: 'statusbar-sep', text: '·' }),
            el('span', { className: 'statusbar-version', text: 'v0.1.0-nightly' })
        ]),
        el('div', { className: 'statusbar-right' }, [
            el('span', { className: 'statusbar-stat', id: 'status-installed', text: '...' }),
            el('span', { className: 'statusbar-sep', text: '·' }),
            el('span', { className: 'statusbar-stat', id: 'status-updates', text: '...' })
        ])
    ]);

    container.appendChild(bar);
    refreshStatusBar();
}

export async function refreshStatusBar() {
    try {
        const apps = await getInstalledApps();
        const count = apps ? apps.length : 0;
        const installedEl = document.getElementById('status-installed');
        if (installedEl) installedEl.textContent = `${count} installed`;

        // Check updates in background (non-blocking)
        getUpdateCount().then(updateCount => {
            const updatesEl = document.getElementById('status-updates');
            if (updatesEl) {
                updatesEl.textContent = updateCount > 0 ? `${updateCount} updates` : 'up to date';
            }
        }).catch(() => {
            const updatesEl = document.getElementById('status-updates');
            if (updatesEl) updatesEl.textContent = 'up to date';
        });
    } catch (e) {
        console.error('StatusBar refresh error:', e);
    }
}
