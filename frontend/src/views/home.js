import { el } from '../utils.js';
import { navigate } from '../router.js';
import { renderURLBar } from '../components/urlbar.js';
import { checkUV, installUV } from '../api.js';
import { showToast } from '../components/toasts.js';

export function renderHome(container) {
    container.innerHTML = '';

    const wrapper = el('div', { className: 'home-wrapper' });

    const hero = el('div', { className: 'home-hero' }, [
        el('div', { className: 'home-hero-icon', html: '⚡' }),
        el('h1', { className: 'home-hero-title', text: 'Thunder' }),
        el('p', { className: 'home-hero-subtitle', text: 'Run any Python app from GitHub instantly' })
    ]);

    const urlSection = el('div', { className: 'home-url-section' });
    renderURLBar(urlSection, {
        onSubmit: (url) => navigate(`/app/${encodeURIComponent(url)}`)
    });

    const uvSection = el('div', { className: 'home-uv-section', id: 'uv-status' });
    renderUVStatus(uvSection);

    wrapper.appendChild(hero);
    wrapper.appendChild(urlSection);
    wrapper.appendChild(uvSection);
    container.appendChild(wrapper);
}

async function renderUVStatus(container) {
    container.innerHTML = '';
    container.appendChild(el('div', { className: 'uv-loading', text: 'Checking uv...' }));

    const { installed, version } = await checkUV();

    container.innerHTML = '';

    if (installed) {
        container.appendChild(el('div', { className: 'uv-status uv-installed' }, [
            el('span', { className: 'uv-status-icon', html: '&#10003;' }),
            el('span', { className: 'uv-status-text', html: `<strong>uv</strong> is ready (${version})` })
        ]));
    } else {
        container.appendChild(el('div', { className: 'uv-status uv-missing' }, [
            el('span', { className: 'uv-status-icon', text: '!' }),
            el('span', { className: 'uv-status-text', html: '<strong>uv</strong> is not installed' }),
            el('button', {
                className: 'btn btn-primary btn-sm',
                text: 'Install uv',
                onClick: async (e) => {
                    e.target.disabled = true;
                    e.target.textContent = 'Installing...';
                    const result = await installUV();
                    if (result.success) {
                        showToast('uv installed successfully!', 'success');
                        renderUVStatus(container);
                    } else {
                        showToast('Failed to install uv: ' + result.error, 'error');
                        e.target.disabled = false;
                        e.target.textContent = 'Install uv';
                    }
                }
            })
        ]));
    }
}
