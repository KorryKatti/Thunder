import { el, formatNumber, escapeHtml } from '../utils.js';
import { navigate } from '../router.js';
import { renderURLBar } from '../components/urlbar.js';
import { fetchRepoInfo, fetchReadme, detectPythonProject, downloadAndInstall, openExternal, onInstallProgress, offInstallProgress, getAvatarUrl } from '../api.js';
import { showToast } from '../components/toasts.js';
import { addDownload, updateDownload, completeDownload } from '../downloads.js';
import { marked } from 'marked';

let currentProjectInfo = null;

export function renderAppDetail(container, encodedURL) {
    container.innerHTML = '';
    currentProjectInfo = null;
    offInstallProgress();

    const url = decodeURIComponent(encodedURL);

    const urlSection = el('div', { className: 'detail-url-section' });
    renderURLBar(urlSection, {
        onSubmit: (newUrl) => navigate(`/app/${encodeURIComponent(newUrl)}`),
        currentURL: url
    });
    container.appendChild(urlSection);

    const contentArea = el('div', { className: 'detail-content', id: 'detail-content' });
    contentArea.appendChild(el('div', { className: 'detail-loading' }, [
        el('div', { className: 'spinner' }),
        el('span', { text: 'Loading repository...' })
    ]));
    container.appendChild(contentArea);

    loadRepoData(contentArea, url);
}

async function loadRepoData(container, url) {
    try {
        const [repoInfo, readme, projectInfo] = await Promise.all([
            fetchRepoInfo(url),
            fetchReadme(url),
            detectPythonProject(url).catch(() => null)
        ]);

        if (!repoInfo) throw new Error('No repository data returned');

        currentProjectInfo = projectInfo;
        container.innerHTML = '';
        renderRepoPage(container, repoInfo, readme, projectInfo, url);
    } catch (e) {
        console.error('Failed to load repo:', e);
        container.innerHTML = '';
        container.appendChild(el('div', { className: 'detail-error' }, [
            el('div', { className: 'detail-error-icon', text: '!' }),
            el('h3', { text: 'Failed to load repository' }),
            el('p', { className: 'detail-error-msg', text: String(e) }),
            el('button', {
                className: 'btn btn-secondary',
                text: 'Back to Home',
                onClick: () => navigate('/')
            })
        ]));
    }
}

function renderRepoPage(container, repo, readme, projectInfo, url) {
    const avatarUrl = getAvatarUrl(url);

    const heroIcon = avatarUrl
        ? el('img', { className: 'detail-hero-icon', src: avatarUrl, alt: repo.Name, onerror: function() { this.style.display = 'none'; this.nextSibling.style.display = 'flex'; } })
        : null;
    const heroIconFallback = el('div', { className: 'detail-hero-icon', text: repo.Name.charAt(0).toUpperCase(), style: avatarUrl ? { display: 'none' } : {} });

    const heroChildren = [heroIcon, heroIconFallback].filter(Boolean);

    const hero = el('div', { className: 'detail-hero' }, [
        el('div', { className: 'detail-hero-bg' }),
        el('div', { className: 'detail-hero-content' }, [
            ...heroChildren,
            el('div', { className: 'detail-hero-info' }, [
                el('p', { className: 'detail-hero-fullname', text: repo.FullName }),
                el('h1', { className: 'detail-hero-name', text: repo.Name }),
                el('p', { className: 'detail-hero-desc', text: repo.Description || 'No description' })
            ])
        ])
    ]);

    // Stats
    const stats = el('div', { className: 'detail-stats' }, [
        createStat('★', formatNumber(repo.Stars), 'Stars'),
        createStat('⑂', formatNumber(repo.Forks), 'Forks'),
        repo.Size ? createStat('📦', formatRepoSize(repo.Size), 'Size') : null,
        repo.Language ? createStat('●', repo.Language, 'Language') : null,
        repo.LicenseName ? createStat('📄', repo.LicenseName, 'License') : null
    ].filter(Boolean));

    // Project info card
    const projectCard = createProjectCard(projectInfo);

    // Install section
    const installSection = el('div', { className: 'detail-install-section' });
    renderInstallButton(installSection, url, repo.Name);

    // README
    let readmeSection = null;
    if (readme) {
        const readmeContent = el('div', {
            className: 'detail-readme-content markdown-body',
            html: marked.parse(readme)
        });

        readmeContent.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link) {
                const href = link.getAttribute('href');
                if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
                    e.preventDefault();
                    openExternal(href);
                }
            }
        });

        readmeSection = el('div', { className: 'detail-readme' }, [
            el('h2', { className: 'detail-section-title', text: 'README' }),
            readmeContent
        ]);
    }

    container.appendChild(hero);
    container.appendChild(stats);
    if (projectCard) container.appendChild(projectCard);
    container.appendChild(installSection);
    if (readmeSection) container.appendChild(readmeSection);
}

function createProjectCard(projectInfo) {
    if (!projectInfo) return null;

    const items = [];

    if (projectInfo.HasPyproject) {
        items.push(el('div', { className: 'project-item project-good' }, [
            el('span', { className: 'project-icon', html: '&#10003;' }),
            el('span', { text: 'pyproject.toml found' })
        ]));
    } else if (projectInfo.HasRequirements) {
        items.push(el('div', { className: 'project-item project-good' }, [
            el('span', { className: 'project-icon', html: '&#10003;' }),
            el('span', { text: `${projectInfo.FileName} found` })
        ]));
    } else {
        items.push(el('div', { className: 'project-item project-warn' }, [
            el('span', { className: 'project-icon', text: '!' }),
            el('span', { text: 'No Python project file detected' })
        ]));
    }

    if (projectInfo.EntryPoint) {
        items.push(el('div', { className: 'project-item' }, [
            el('span', { className: 'project-icon', text: '▸' }),
            el('span', { html: `Entry point: <strong>${projectInfo.EntryPoint}</strong>` })
        ]));
    }

    if (projectInfo.FileSize > 0) {
        items.push(el('div', { className: 'project-item' }, [
            el('span', { className: 'project-icon', text: '▸' }),
            el('span', { text: `Config file: ${formatFileSize(projectInfo.FileSize)}` })
        ]));
    }

    return el('div', { className: 'detail-project-card' }, [
        el('h3', { className: 'detail-project-title', text: 'Python Project' }),
        el('div', { className: 'detail-project-items' }, items)
    ]);
}

const stepLabels = {
    info: 'Preparing...',
    download: 'Downloading repository...',
    extract: 'Extracting files...',
    detect: 'Detecting project type...',
    venv: 'Creating virtual environment...',
    deps: 'Installing dependencies...',
    done: 'Complete!'
};

function renderInstallButton(container, url, repoName) {
    const progressBar = el('div', { className: 'install-progress', style: { display: 'none' } }, [
        el('div', { className: 'install-progress-bar' }),
        el('span', { className: 'install-progress-text', text: '' })
    ]);

    const btn = el('button', {
        className: 'btn btn-green btn-lg install-btn',
        text: 'Download & Install',
        onClick: async () => {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-inline"></span> Starting...';
            progressBar.style.display = 'block';

            const dlId = addDownload(repoName, url);

            onInstallProgress((data) => {
                if (data.percent) {
                    const pct = parseInt(data.percent);
                    progressBar.querySelector('.install-progress-bar').style.width = pct + '%';
                    progressBar.querySelector('.install-progress-text').textContent = `Downloading... ${pct}%`;
                    btn.innerHTML = `<span class="spinner-inline"></span> Downloading... ${pct}%`;
                    updateDownload(dlId, `Downloading... ${pct}%`);
                } else {
                    const label = stepLabels[data.step] || data.message;
                    btn.innerHTML = `<span class="spinner-inline"></span> ${label}`;
                    updateDownload(dlId, label);
                }
            });

            const result = await downloadAndInstall(url);
            offInstallProgress();

            if (result.success) {
                completeDownload(dlId, true);
                showToast(`${repoName} installed successfully!`, 'success');
                btn.textContent = 'Installed';
                btn.classList.add('installed');
            } else {
                completeDownload(dlId, false, result.error);
                showToast('Install failed: ' + result.error, 'error');
                btn.disabled = false;
                btn.textContent = 'Download & Install';
            }
        }
    });

    const actions = el('div', { className: 'detail-actions' }, [
        btn,
        el('button', {
            className: 'btn btn-secondary btn-lg',
            text: 'View on GitHub',
            onClick: () => openExternal(url)
        })
    ]);

    container.appendChild(actions);
    container.appendChild(progressBar);
}

function createStat(icon, value, label) {
    return el('div', { className: 'detail-stat' }, [
        el('span', { className: 'detail-stat-icon', text: icon }),
        el('span', { className: 'detail-stat-value', text: value }),
        el('span', { className: 'detail-stat-label', text: label })
    ]);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatRepoSize(kb) {
    if (kb < 1024) return kb + ' KB';
    if (kb < 1024 * 1024) return (kb / 1024).toFixed(1) + ' MB';
    return (kb / (1024 * 1024)).toFixed(1) + ' GB';
}
