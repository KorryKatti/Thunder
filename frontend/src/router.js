const routes = [];
let currentRoute = null;
let notFoundHandler = null;

export function addRoute(pattern, handler) {
    const paramNames = [];
    const regexStr = pattern.replace(/:(\w+)/g, (_, name) => {
        paramNames.push(name);
        return '([^/]+)';
    });
    routes.push({
        pattern,
        regex: new RegExp(`^${regexStr}$`),
        paramNames,
        handler
    });
}

export function setNotFound(handler) {
    notFoundHandler = handler;
}

export function navigate(path) {
    window.location.hash = path;
}

export function getCurrentPath() {
    return window.location.hash.slice(1) || '/';
}

function resolve() {
    const path = getCurrentPath();

    for (const route of routes) {
        const match = path.match(route.regex);
        if (match) {
            const params = {};
            route.paramNames.forEach((name, i) => {
                params[name] = decodeURIComponent(match[i + 1]);
            });
            currentRoute = { path, params, pattern: route.pattern };
            route.handler(params);
            return;
        }
    }

    currentRoute = { path, params: {}, pattern: null };
    if (notFoundHandler) {
        notFoundHandler(path);
    }
}

export function getCurrentRoute() {
    return currentRoute;
}

export function initRouter() {
    window.addEventListener('hashchange', resolve);
    resolve();
}
