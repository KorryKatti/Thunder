import { el } from '../utils.js';

export function renderSettings(container) {
    container.innerHTML = '';

    const header = el('div', { className: 'view-header' }, [
        el('h1', { className: 'view-title', text: 'Settings' }),
        el('p', { className: 'view-subtitle', text: 'Configure Thunder' })
    ]);

    const sections = el('div', { className: 'settings-sections' }, [
        createSection('General', [
            createSettingRow('Install Directory', 'path', '~/.thunder-nightly/apps', 'Where apps are installed'),
            createSettingRow('Python Path', 'text', '/usr/bin/python3', 'Path to Python interpreter')
        ]),
        createSection('GitHub', [
            createSettingRow('Personal Access Token', 'password', '', 'For higher API rate limits (optional)', 'Test Connection')
        ]),
        createSection('Advanced', [
            createDangerRow('Clear Cache', 'Remove all cached data', 'Clear Cache'),
            createDangerRow('Reset All Data', 'Remove all apps and settings', 'Reset')
        ]),
        createSection('About', [
            el('div', { className: 'settings-about' }, [
                el('div', { className: 'settings-about-row' }, [
                    el('span', { className: 'settings-about-label', text: 'Version' }),
                    el('span', { className: 'settings-about-value mono', text: 'v0.1.0-nightly' })
                ]),
                el('div', { className: 'settings-about-row' }, [
                    el('span', { className: 'settings-about-label', text: 'License' }),
                    el('span', { className: 'settings-about-value', text: 'MIT' })
                ]),
                el('div', { className: 'settings-about-row' }, [
                    el('span', { className: 'settings-about-label', text: 'Repository' }),
                    el('a', { className: 'settings-about-link', href: 'https://github.com/korrykatti/thunder-nightly', text: 'GitHub' })
                ])
            ])
        ])
    ]);

    container.appendChild(header);
    container.appendChild(sections);
}

function createSection(title, children) {
    return el('div', { className: 'settings-section' }, [
        el('h2', { className: 'settings-section-title', text: title }),
        el('div', { className: 'settings-section-content' }, children)
    ]);
}

function createSettingRow(label, type, value, description, actionLabel) {
    const input = el('input', {
        className: 'settings-input',
        type: type === 'password' ? 'password' : 'text',
        value: value || '',
        placeholder: description
    });

    const children = [
        el('div', { className: 'settings-row' }, [
            el('div', { className: 'settings-row-info' }, [
                el('label', { className: 'settings-label', text: label }),
                el('p', { className: 'settings-desc', text: description })
            ]),
            el('div', { className: 'settings-row-control' }, [
                input,
                actionLabel ? el('button', {
                    className: 'btn btn-secondary btn-sm',
                    text: actionLabel,
                    onClick: () => console.log('Action:', label)
                }) : null
            ].filter(Boolean))
        ])
    ];

    return el('div', {}, children);
}

function createDangerRow(label, description, actionLabel) {
    return el('div', { className: 'settings-row settings-row-danger' }, [
        el('div', { className: 'settings-row-info' }, [
            el('label', { className: 'settings-label', text: label }),
            el('p', { className: 'settings-desc', text: description })
        ]),
        el('button', {
            className: 'btn btn-danger btn-sm',
            text: actionLabel,
            onClick: () => console.log('Danger action:', label)
        })
    ]);
}
