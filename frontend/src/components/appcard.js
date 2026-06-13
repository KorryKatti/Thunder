import { el, formatNumber, escapeHtml } from '../utils.js';
import { navigate } from '../router.js';

export function createAppCard(app) {
    const card = el('div', { className: 'app-card', 'data-app-id': app.id });

    const iconEl = app.iconUrl
        ? el('img', { className: 'app-card-icon', src: app.iconUrl, alt: app.name })
        : el('div', { className: 'app-card-icon app-card-icon-fallback', text: app.name.charAt(0).toUpperCase() });

    const installBtn = app.installed
        ? el('button', { className: 'app-card-badge installed', text: 'Installed' })
        : el('button', {
            className: 'app-card-install-btn',
            text: 'Install',
            onClick: (e) => {
                e.stopPropagation();
                installApp(app);
            }
        });

    const cardInner = el('div', { className: 'app-card-inner' }, [
        el('div', { className: 'app-card-image' }, [
            iconEl,
            el('div', { className: 'app-card-image-overlay' })
        ]),
        el('div', { className: 'app-card-body' }, [
            el('h3', { className: 'app-card-title', text: app.name }),
            el('p', { className: 'app-card-desc', text: app.description || 'No description' }),
            el('div', { className: 'app-card-meta' }, [
                el('span', { className: 'app-card-stars', html: `★ ${formatNumber(app.stars || 0)}` }),
                app.language ? el('span', { className: 'app-card-lang', text: app.language }) : null,
                el('span', { className: 'app-card-price', text: 'Free' })
            ]),
            el('div', { className: 'app-card-footer' }, [installBtn])
        ])
    ]);

    card.appendChild(cardInner);

    card.addEventListener('click', () => {
        navigate(`/store/${app.id}`);
    });

    return card;
}

function installApp(app) {
    const btn = document.querySelector(`[data-app-id="${app.id}"] .app-card-install-btn`);
    if (btn) {
        btn.textContent = 'Installing...';
        btn.disabled = true;
    }
    // Will be connected to Go backend in Phase 2
    console.log('Install:', app.repo);
}

export function createSkeletonCard() {
    return el('div', { className: 'app-card skeleton' }, [
        el('div', { className: 'app-card-inner' }, [
            el('div', { className: 'app-card-image skeleton-pulse' }),
            el('div', { className: 'app-card-body' }, [
                el('div', { className: 'skeleton-text skeleton-pulse', style: { width: '60%', height: '16px' } }),
                el('div', { className: 'skeleton-text skeleton-pulse', style: { width: '100%', height: '12px', marginTop: '8px' } }),
                el('div', { className: 'skeleton-text skeleton-pulse', style: { width: '40%', height: '12px', marginTop: '4px' } }),
                el('div', { className: 'skeleton-text skeleton-pulse', style: { width: '30%', height: '12px', marginTop: '12px' } })
            ])
        ])
    ]);
}
