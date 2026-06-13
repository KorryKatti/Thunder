import { el } from '../utils.js';

let toastContainer = null;

function ensureContainer() {
    if (!toastContainer) {
        toastContainer = el('div', { className: 'toast-container', id: 'toast-container' });
        document.body.appendChild(toastContainer);
    }
    return toastContainer;
}

export function showToast(message, type = 'info', duration = 3000) {
    const container = ensureContainer();

    const iconMap = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    const toast = el('div', { className: `toast toast-${type}` }, [
        el('span', { className: 'toast-icon', text: iconMap[type] || iconMap.info }),
        el('span', { className: 'toast-message', text: message }),
        el('button', {
            className: 'toast-close',
            text: '✕',
            onClick: () => removeToast(toast)
        })
    ]);

    container.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('toast-visible'));

    if (duration > 0) {
        setTimeout(() => removeToast(toast), duration);
    }

    return toast;
}

function removeToast(toast) {
    toast.classList.remove('toast-visible');
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
}
