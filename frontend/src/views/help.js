import { el } from '../utils.js';
import { openExternal } from '../api.js';
import inspoImg from '../assets/images/inspo.png';

export function renderHelp(container) {
    container.innerHTML = '';

    const sections = [
        {
            title: 'What is Thunder?',
            content: 'Thunder is a desktop app launcher for Python programs hosted on GitHub. Paste a GitHub URL, and Thunder will download, install, and launch the app for you — complete with its own virtual environment.'
        },
        {
            title: 'Getting Started',
            steps: [
                'Go to the Home screen and paste a GitHub URL (e.g. https://github.com/owner/repo)',
                'Thunder will detect the Python project and show you the entry point',
                'Click "Download & Install" to download the repo, create a venv, and install dependencies',
                'Once installed, go to Library to launch, configure, or uninstall apps'
            ]
        },
        {
            title: 'How Installation Works',
            items: [
                'Thunder downloads the repo as a zip file',
                'Extracts it to ~/.thunder-nightly/apps/repo-name/',
                'Creates a Python virtual environment using uv',
                'Installs dependencies from pyproject.toml, requirements.txt, or setup.py',
                'Saves app metadata to ~/.thunder-nightly/index.json',
                'Auto-detects the entry point (main.py, app.py, etc.)'
            ]
        },
        {
            title: 'Launch Types',
            items: [
                'GUI: Launches the app directly (for tkinter, PyQt, pygame apps)',
                'CLI: Opens a terminal window to run the app (for command-line tools)',
                'Auto: Thunder detects whether the app needs a terminal based on imports',
                'You can toggle the launch type per-app in the Library'
            ]
        },
        {
            title: 'App Configuration',
            items: [
                'Click "Config" in Library to auto-detect and save entry point + Python version',
                'Click the launch type badge to cycle: Auto → GUI → CLI',
                'Thunder stores config in .thunder.json inside each app folder'
            ]
        },
        {
            title: 'Requirements',
            items: [
                'Python 3.x installed on your system',
                'uv (Python package manager) — Thunder can install it for you',
                'git (for update checking)',
                'A terminal emulator (for CLI apps on Linux/macOS)'
            ]
        },
        {
            title: 'File Locations',
            items: [
                '~/.thunder-nightly/index.json — registry of all installed apps',
                '~/.thunder-nightly/apps/ — installed app directories',
                '~/.thunder-nightly/downloading/ — temporary download folder',
                'Each app has its own venv/ and .thunder.json config'
            ]
        },
        {
            title: 'Troubleshooting',
            items: [
                'App won\'t launch? Try toggling the launch type (GUI/CLI)',
                'Entry point wrong? Click "Config" to re-detect, or check .thunder.json',
                'Install fails? Make sure Python and uv are installed and working',
                'CLI app shows nothing? It might need a terminal — switch launch type to CLI'
            ]
        }
    ];

    const hero = el('div', { className: 'help-hero' }, [
        el('h1', { className: 'view-title', text: 'Help & Documentation' }),
        el('p', { className: 'view-subtitle', text: 'Everything you need to know about using Thunder' })
    ]);

    container.appendChild(hero);

    sections.forEach(section => {
        const sectionEl = el('div', { className: 'help-section' }, [
            el('h2', { className: 'help-section-title', text: section.title })
        ]);

        if (section.content) {
            sectionEl.appendChild(el('p', { className: 'help-section-text', text: section.content }));
        }

        if (section.steps) {
            const ol = el('ol', { className: 'help-steps' });
            section.steps.forEach(step => {
                ol.appendChild(el('li', { text: step }));
            });
            sectionEl.appendChild(ol);
        }

        if (section.items) {
            const ul = el('ul', { className: 'help-list' });
            section.items.forEach(item => {
                ul.appendChild(el('li', { text: item }));
            });
            sectionEl.appendChild(ul);
        }

        container.appendChild(sectionEl);
    });

    // Inspiration
    container.appendChild(el('div', { className: 'help-section' }, [
        el('h2', { className: 'help-section-title', text: 'Inspiration' }),
        el('p', { className: 'help-section-text', text: 'Thunder was born from this viral Reddit post about the struggle of using GitHub as a non-developer:' }),
        el('div', { className: 'help-inspo-quote' }, [
            el('blockquote', { className: 'help-blockquote', html: '"I DONT GIVE A FUCK ABOUT THE FUCKING CODE! i just want to download this stupid fucking application and use it... WHY IS THERE CODE??? MAKE A FUCKING .EXE FILE AND GIVE IT TO ME." — u/automatic_purpose_ on r/github' })
        ]),
        el('p', { className: 'help-section-text', text: 'Thunder exists so nobody has to feel this way again. Paste a link, click install, done.' }),
        el('div', { className: 'help-inspo' }, [
            el('img', { className: 'help-inspo-img', src: inspoImg, alt: 'Reddit post that inspired Thunder' })
        ])
    ]));

    // Footer link
    container.appendChild(el('div', { className: 'help-footer' }, [
        el('p', { text: 'Found a bug? Have a suggestion?' }),
        el('button', {
            className: 'btn btn-secondary',
            text: 'Open GitHub Repository',
            onClick: () => openExternal('https://github.com/korrykatti/thunder-nightly')
        })
    ]));
}
