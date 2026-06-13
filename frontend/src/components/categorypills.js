import { el } from '../utils.js';
import { getState, setState, subscribe } from '../state.js';

const categories = [
    { id: 'all', label: 'All' },
    { id: 'ai-ml', label: 'AI/ML' },
    { id: 'cli', label: 'CLI' },
    { id: 'web', label: 'Web' },
    { id: 'science', label: 'Science' },
    { id: 'tools', label: 'Tools' },
    { id: 'other', label: 'Other' }
];

export function renderCategoryPills(container, { onSelect } = {}) {
    const wrapper = el('div', { className: 'category-pills' });

    categories.forEach(cat => {
        const pill = el('button', {
            className: 'category-pill',
            'data-category': cat.id,
            text: cat.label,
            onClick: () => {
                setState('selectedCategory', cat.id);
                updatePillStates(wrapper);
                if (onSelect) onSelect(cat.id);
            }
        });
        wrapper.appendChild(pill);
    });

    container.appendChild(wrapper);
    updatePillStates(wrapper);
}

function updatePillStates(wrapper) {
    const current = getState('selectedCategory');
    wrapper.querySelectorAll('.category-pill').forEach(pill => {
        pill.classList.toggle('active', pill.getAttribute('data-category') === current);
    });
}
