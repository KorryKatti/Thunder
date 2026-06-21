import { el } from '../utils.js';
import { getSettings, updateSettings, clearCache, resetAllData } from '../api.js';
import { showToast } from '../components/toasts.js';

let currentSettings = {};

export async function renderSettings(container) {
    container.innerHTML = '';

    const header = el('div', { className: 'view-header' }, [
        el('h1', { className: 'view-title', text: 'Settings' }),
        el('p', { className: 'view-subtitle', text: 'Configure Thunder' })
    ]);

    currentSettings = await getSettings();

    const sections = el('div', { className: 'settings-sections' }, [
        createSection('General', [
            createSettingRow('Install Directory', 'text', currentSettings.install_dir || '~/.thunder-nightly/apps', 'Where apps are installed', async (val) => {
                const result = await updateSettings('', val, '');
                if (result.success) showToast('Install directory updated', 'success');
                else showToast('Failed: ' + result.error, 'error');
            }),
            createSettingRow('Python Path', 'text', currentSettings.python_path || '', 'Path to Python interpreter (leave empty for auto-detect)', async (val) => {
                const result = await updateSettings('', '', val);
                if (result.success) showToast('Python path updated', 'success');
                else showToast('Failed: ' + result.error, 'error');
            })
        ]),
        createSection('GitHub', [
            createSettingRow('Personal Access Token', 'password', currentSettings.github_token || '', 'For higher API rate limits (optional)', async (val) => {
                const result = await updateSettings(val, '', '');
                if (result.success) showToast('GitHub token saved', 'success');
                else showToast('Failed: ' + result.error, 'error');
            })
        ]),
        createSection('Advanced', [
            createDangerRow('Clear Cache', 'Remove all cached downloads', 'Clear Cache', async () => {
                const result = await clearCache();
                if (result.success) showToast('Cache cleared', 'success');
                else showToast('Failed: ' + result.error, 'error');
            }),
            createDangerRow('Reset All Data', 'Remove all apps and settings', 'Reset', async () => {
                if (!confirm('This will delete ALL installed apps and settings. Continue?')) return;
                const result = await resetAllData();
                if (result.success) {
                    showToast('All data reset', 'success');
                    currentSettings = {};
                } else {
                    showToast('Failed: ' + result.error, 'error');
                }
            })
        ]),
        createSection('About', [
            el('div', { className: 'settings-about' }, [
                el('div', { className: 'settings-about-row' }, [
                    el('span', { className: 'settings-about-label', text: 'Version' }),
                    el('span', { className: 'settings-about-value mono', text: 'v0.1.0-stable' })
                ]),
                el('div', { className: 'settings-about-row' }, [
                    el('span', { className: 'settings-about-label', text: 'License' }),
                    el('span', { className: 'settings-about-value', text: 'MIT' })
                ]),
                el('div', { className: 'settings-about-row' }, [
                    el('span', { className: 'settings-about-label', text: 'Repository' }),
                    el('button', { className: 'settings-about-link', text: 'GitHub', onClick: () => openExternal('https://github.com/korrykatti/thunder-nightly') })
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

function createSettingRow(label, type, value, description, onSave) {
    const input = el('input', {
        className: 'settings-input',
        type: type === 'password' ? 'password' : 'text',
        value: value || '',
        placeholder: description
    });

    const saveBtn = el('button', {
        className: 'btn btn-secondary btn-sm',
        text: 'Save',
        onClick: async () => {
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            await onSave(input.value);
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save';
        }
    });

    return el('div', { className: 'settings-row' }, [
        el('div', { className: 'settings-row-info' }, [
            el('label', { className: 'settings-label', text: label }),
            el('p', { className: 'settings-desc', text: description })
        ]),
        el('div', { className: 'settings-row-control' }, [
            input,
            saveBtn
        ])
    ]);
}

function createDangerRow(label, description, actionLabel, onAction) {
    return el('div', { className: 'settings-row settings-row-danger' }, [
        el('div', { className: 'settings-row-info' }, [
            el('label', { className: 'settings-label', text: label }),
            el('p', { className: 'settings-desc', text: description })
        ]),
        el('button', {
            className: 'btn btn-danger btn-sm',
            text: actionLabel,
            onClick: async (e) => {
                e.target.disabled = true;
                e.target.textContent = 'Working...';
                await onAction();
                e.target.disabled = false;
                e.target.textContent = actionLabel;
            }
        })
    ]);
}
