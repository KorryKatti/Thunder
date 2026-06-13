import { el } from '../utils.js';

export function renderURLBar(container, { onSubmit, currentURL = '' } = {}) {
    const input = el('input', {
        className: 'urlbar-input',
        type: 'text',
        placeholder: 'Paste a GitHub URL — e.g. https://github.com/owner/repo',
        value: currentURL,
        id: 'urlbar-input'
    });

    const goBtn = el('button', {
        className: 'urlbar-go',
        text: 'Go',
        onClick: () => {
            const url = input.value.trim();
            if (url && onSubmit) onSubmit(url);
        }
    });

    const clearBtn = el('button', {
        className: 'urlbar-clear',
        html: '&times;',
        onClick: () => {
            input.value = '';
            input.focus();
        }
    });

    const wrapper = el('div', { className: 'urlbar' }, [
        el('span', { className: 'urlbar-icon', html: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>` }),
        input,
        clearBtn,
        goBtn
    ]);

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const url = input.value.trim();
            if (url && onSubmit) onSubmit(url);
        }
    });

    container.appendChild(wrapper);
    return { input, wrapper };
}
