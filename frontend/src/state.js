const state = {
    apps: [],
    installed: [],
    currentView: 'home',
    searchQuery: '',
    selectedCategory: 'all',
    isLoading: false,
    settings: {
        installDir: '',
        pythonPath: '',
        githubToken: ''
    }
};

const listeners = {};

export function getState(key) {
    return key ? state[key] : { ...state };
}

export function setState(key, value) {
    if (typeof key === 'object') {
        Object.assign(state, key);
        Object.keys(key).forEach(k => notify(k));
    } else {
        state[key] = value;
        notify(key);
    }
}

export function subscribe(key, fn) {
    if (!listeners[key]) listeners[key] = [];
    listeners[key].push(fn);
    return () => {
        listeners[key] = listeners[key].filter(f => f !== fn);
    };
}

function notify(key) {
    if (listeners[key]) {
        listeners[key].forEach(fn => fn(state[key], state));
    }
    if (listeners['*']) {
        listeners['*'].forEach(fn => fn(state));
    }
}
