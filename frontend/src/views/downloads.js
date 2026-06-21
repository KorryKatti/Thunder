import { el } from '../utils.js';
import { getDownloads, onDownloadsChange } from '../downloads.js';

export function renderDownloads(container) {
    container.innerHTML = '';

    const header = el('div', { className: 'view-header' }, [
        el('h1', { className: 'view-title', text: 'Downloads' }),
        el('p', { className: 'view-subtitle', text: 'Active and recent installs' })
    ]);

    const list = el('div', { className: 'downloads-list', id: 'downloads-list' });
    container.appendChild(header);
    container.appendChild(list);

    function refresh() { renderList(list, getDownloads()); }
    refresh();
    const unsub = onDownloadsChange(refresh);

    // Clean up on re-render
    const origEmpty = container.innerHTML;
    const observer = new MutationObserver(() => {
        if (!document.getElementById('downloads-list')) { unsub(); observer.disconnect(); }
    });
    observer.observe(container, { childList: true });
}

function renderList(container, items) {
    container.innerHTML = '';

    if (!items.length) {
        container.appendChild(el('div', { className: 'empty-state' }, [
            el('div', { className: 'empty-state-icon', html: '&#128229;' }),
            el('h3', { className: 'empty-state-title', text: 'No downloads yet' }),
            el('p', { className: 'empty-state-desc', text: 'Install an app and it will appear here' })
        ]));
        return;
    }

    items.forEach(d => {
        const isActive = d.status === 'active';
        const isFailed = d.status === 'failed';
        const icon = isActive ? '<span class="spinner-inline"></span>' : isFailed ? '&#10005;' : '&#10003;';
        const statusClass = isActive ? 'download-active' : isFailed ? 'download-failed' : 'download-done';

        container.appendChild(el('div', { className: `download-row ${statusClass}` }, [
            el('span', { className: 'download-icon', html: icon }),
            el('div', { className: 'download-info' }, [
                el('div', { className: 'download-name', text: d.name || d.url }),
                el('div', { className: 'download-step', text: d.step })
            ]),
            el('span', { className: 'download-time', text: formatTime(d.time) })
        ]));
    });
}

function formatTime(t) {
    if (!t) return '';
    const d = new Date(t);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
