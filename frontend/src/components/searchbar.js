import { el, debounce } from '../utils.js';
import { setState } from '../state.js';

export function renderSearchBar(container, { onSearch, placeholder = 'Search apps on Thunder...' } = {}) {
    const input = el('input', {
        className: 'search-input',
        type: 'text',
        placeholder,
        id: 'search-input'
    });

    const icon = el('span', {
        className: 'search-icon',
        html: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`
    });

    const wrapper = el('div', { className: 'search-bar' }, [icon, input]);
    container.appendChild(wrapper);

    const debouncedSearch = debounce((value) => {
        setState('searchQuery', value);
        if (onSearch) onSearch(value);
    }, 300);

    input.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            input.value = '';
            input.blur();
            debouncedSearch('');
        }
    });

    return { input, wrapper };
}
