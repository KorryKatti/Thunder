import { el } from '../utils.js';
import { navigate } from '../router.js';
import { renderURLBar } from '../components/urlbar.js';
import { checkUV, installUV, getAvatarUrl, getInstalledApps } from '../api.js';
import { showToast } from '../components/toasts.js';

const featuredApps = [
    {
        name: 'Evidex',
        url: 'https://github.com/jyun-lab/Evidex',
        description: 'Local-first desktop app for searchable experiment records, linked lab files, and CSV waveform previews.',
        tags: ['Science', 'Data']
    },
    {
        name: 'python-tkinter-calculator',
        url: 'https://github.com/LasyaGanesuni/python-tkinter-calculator',
        description: 'A simple GUI calculator made with Python and tkinter.',
        tags: ['GUI', 'Tool']
    }
];

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

    const featuredSection = el('div', { className: 'home-featured' });
    renderFeaturedApps(featuredSection);

    wrapper.appendChild(hero);
    wrapper.appendChild(urlSection);
    wrapper.appendChild(uvSection);
    wrapper.appendChild(featuredSection);
    container.appendChild(wrapper);
}

async function renderFeaturedApps(container) {
    const installed = await getInstalledApps();
    const installedUrls = new Set(installed.map(a => a.url));

    const header = el('div', { className: 'home-section-header' }, [
        el('h2', { className: 'home-section-title', text: 'Featured Apps' }),
        el('button', {
            className: 'home-section-more',
            text: 'View all',
            onClick: () => navigate('/library')
        })
    ]);

    const grid = el('div', { className: 'home-featured-grid' },
        featuredApps.map(app => {
            const isInstalled = installedUrls.has(app.url);
            const avatarUrl = getAvatarUrl(app.url);

            const avatar = avatarUrl
                ? el('img', { className: 'featured-card-avatar', src: avatarUrl, alt: app.name, onerror: function() { this.style.display = 'none'; this.nextSibling.style.display = 'flex'; } })
                : null;
            const fallback = el('div', {
                className: 'featured-card-icon',
                text: app.name.charAt(0).toUpperCase(),
                style: avatarUrl ? { display: 'none' } : {}
            });

            return el('div', { className: 'featured-card', onClick: () => navigate(`/app/${encodeURIComponent(app.url)}`) }, [
                ...([avatar, fallback].filter(Boolean)),
                el('div', { className: 'featured-card-info' }, [
                    el('h3', { className: 'featured-card-name', text: app.name }),
                    el('p', { className: 'featured-card-desc', text: app.description }),
                    el('div', { className: 'featured-card-tags' },
                        app.tags.map(t => el('span', { className: 'featured-tag', text: t }))
                    )
                ]),
                el('span', {
                    className: isInstalled ? 'featured-card-badge installed' : 'featured-card-badge',
                    text: isInstalled ? 'Installed' : 'Install'
                })
            ]);
        })
    );

    container.appendChild(header);
    container.appendChild(grid);
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
