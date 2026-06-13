import { el } from '../utils.js';

const COMMUNITY_URL = 'https://korrykatti.pythonanywhere.com/';

export function renderCommunity(container) {
    container.innerHTML = '';

    const header = el('div', { className: 'view-header' }, [
        el('h1', { className: 'view-title', text: 'Community' }),
        el('p', { className: 'view-subtitle', text: 'Join the Thunder community' })
    ]);

    const frame = el('iframe', {
        className: 'community-frame',
        src: COMMUNITY_URL,
        frameborder: '0',
        allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
    });

    container.appendChild(header);
    container.appendChild(frame);
}
