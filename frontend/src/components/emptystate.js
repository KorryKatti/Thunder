import { el } from '../utils.js';

const illustrations = {
    empty: `<svg width="120" height="120" viewBox="0 0 120 120" fill="none"><circle cx="60" cy="60" r="50" stroke="#3D5A80" stroke-width="2" stroke-dasharray="4 4"/><path d="M45 55 L55 65 L75 45" stroke="#66C0F4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/></svg>`,
    search: `<svg width="120" height="120" viewBox="0 0 120 120" fill="none"><circle cx="52" cy="52" r="28" stroke="#3D5A80" stroke-width="2"/><line x1="72" y1="72" x2="90" y2="90" stroke="#3D5A80" stroke-width="3" stroke-linecap="round"/><line x1="44" y1="52" x2="60" y2="52" stroke="#66C0F4" stroke-width="2" stroke-linecap="round"/><line x1="52" y1="44" x2="52" y2="60" stroke="#66C0F4" stroke-width="2" stroke-linecap="round"/></svg>`,
    library: `<svg width="120" height="120" viewBox="0 0 120 120" fill="none"><rect x="25" y="30" width="70" height="60" rx="4" stroke="#3D5A80" stroke-width="2"/><line x1="35" y1="45" x2="85" y2="45" stroke="#66C0F4" stroke-width="2" stroke-linecap="round" opacity="0.5"/><line x1="35" y1="55" x2="70" y2="55" stroke="#66C0F4" stroke-width="2" stroke-linecap="round" opacity="0.3"/><line x1="35" y1="65" x2="78" y2="65" stroke="#66C0F4" stroke-width="2" stroke-linecap="round" opacity="0.3"/></svg>`
};

export function renderEmptyState(container, { type = 'empty', title, description, action } = {}) {
    const state = el('div', { className: 'empty-state' }, [
        el('div', { className: 'empty-state-icon', html: illustrations[type] || illustrations.empty }),
        el('h3', { className: 'empty-state-title', text: title || 'Nothing here yet' }),
        el('p', { className: 'empty-state-desc', text: description || '' }),
        action ? el('button', {
            className: 'empty-state-action',
            text: action.label,
            onClick: action.handler
        }) : null
    ].filter(Boolean));

    container.appendChild(state);
    return state;
}
