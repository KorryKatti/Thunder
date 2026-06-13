import { el } from '../utils.js';
import { getState, setState, subscribe } from '../state.js';
import { renderSearchBar } from '../components/searchbar.js';
import { renderCategoryPills } from '../components/categorypills.js';
import { createAppCard, createSkeletonCard } from '../components/appcard.js';
import { renderEmptyState } from '../components/emptystate.js';

const mockApps = [
    { id: 'autogpt', name: 'AutoGPT', description: 'Autonomous GPT-4 experiment — give it a goal and it will try to achieve it', stars: 165000, language: 'Python', installed: false },
    { id: 'open-interpreter', name: 'Open Interpreter', description: 'Natural language interface for computers — run code locally', stars: 53000, language: 'Python', installed: true },
    { id: 'comfyui', name: 'ComfyUI', description: 'Most powerful and modular Stable Diffusion GUI and backend', stars: 65000, language: 'Python', installed: false },
    { id: 'stable-diffusion-webui', name: 'Stable Diffusion WebUI', description: 'Stable Diffusion web UI — text to image generation', stars: 145000, language: 'Python', installed: false },
    { id: 'langchain', name: 'LangChain', description: 'Building applications with LLMs through composability', stars: 97000, language: 'Python', installed: false },
    { id: 'private-gpt', name: 'PrivateGPT', description: 'Interact with your documents using LLMs — 100% privately',  stars: 54000, language: 'Python', installed: false },
    { id: 'whisper', name: 'Whisper', description: 'Robust speech recognition via large-scale weak supervision', stars: 72000, language: 'Python', installed: false },
    { id: 'ollama', name: 'Ollama', description: 'Get up and running with large language models locally', stars: 108000, language: 'Python', installed: false },
    { id: 'llama.cpp', name: 'llama.cpp', description: 'Port of Meta\'s LLaMA model in C/C++ — fast inference', stars: 71000, language: 'C++', installed: false },
    { id: 'text-generation-webui', name: 'text-generation-webui', description: 'Gradio UI for running LLMs locally with multiple backend support', stars: 40000, language: 'Python', installed: false },
    { id: 'kohya-ss', name: 'kohya_ss', description: 'GUI for Kohya\'s Stable Diffusion training — LoRA, DreamBooth', stars: 22000, language: 'Python', installed: false },
    { id: 'fooocus', name: 'Fooocus', description: 'Most Stable Diffusion fork — image generating, focused on quality', stars: 41000, language: 'Python', installed: false }
];

export function renderStore(container) {
    container.innerHTML = '';

    const header = el('div', { className: 'view-header' }, [
        el('h1', { className: 'view-title', text: 'Store' }),
        el('p', { className: 'view-subtitle', text: 'Browse and install open-source Python apps' })
    ]);

    const filtersBar = el('div', { className: 'store-filters' });
    renderSearchBar(filtersBar, {
        onSearch: (query) => filterApps(container)
    });
    renderCategoryPills(filtersBar, {
        onSelect: () => filterApps(container)
    });

    const gridContainer = el('div', { className: 'store-grid-container' });

    container.appendChild(header);
    container.appendChild(filtersBar);
    container.appendChild(gridContainer);

    renderAppGrid(gridContainer, mockApps);
}

function renderAppGrid(container, apps) {
    container.innerHTML = '';

    if (apps.length === 0) {
        renderEmptyState(container, {
            type: 'search',
            title: 'No apps found',
            description: 'Try a different search term or category'
        });
        return;
    }

    const grid = el('div', { className: 'store-grid' },
        apps.map(app => createAppCard(app))
    );

    container.appendChild(grid);
}

function filterApps(container) {
    const query = getState('searchQuery').toLowerCase();
    const category = getState('selectedCategory');

    let filtered = mockApps;

    if (query) {
        filtered = filtered.filter(app =>
            app.name.toLowerCase().includes(query) ||
            (app.description && app.description.toLowerCase().includes(query))
        );
    }

    // Category filtering would use real data from Go backend
    // For now, mock data is all Python, so category filter is limited

    const gridContainer = container.querySelector('.store-grid-container');
    if (gridContainer) {
        renderAppGrid(gridContainer, filtered);
    }
}
