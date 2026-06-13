import './style.css';
import './app.css';
import './components.css';

import { addRoute, initRouter, navigate } from './router.js';
import { setState } from './state.js';
import { renderSidebar } from './components/sidebar.js';
import { renderStatusBar, refreshStatusBar } from './components/statusbar.js';
import { renderHome } from './views/home.js';
import { renderAppDetail } from './views/appdetail.js';
import { renderLibrary } from './views/library.js';
import { renderSettings } from './views/settings.js';
import { renderHelp } from './views/help.js';
import { renderCommunity } from './views/community.js';

function renderApp() {
    const app = document.getElementById('app');
    app.innerHTML = '';

    const body = document.createElement('div');
    body.className = 'app-body';

    const sidebarContainer = document.createElement('div');
    sidebarContainer.className = 'sidebar-container';

    const mainContent = document.createElement('div');
    mainContent.className = 'main-content';
    mainContent.id = 'main-content';

    body.appendChild(sidebarContainer);
    body.appendChild(mainContent);
    app.appendChild(body);

    renderSidebar(sidebarContainer);
    renderStatusBar(app);

    addRoute('/', (params) => {
        setState('currentView', 'home');
        renderHome(mainContent);
    });

    addRoute('/app/:url', (params) => {
        setState('currentView', 'app');
        renderAppDetail(mainContent, params.url);
    });

    addRoute('/library', (params) => {
        setState('currentView', 'library');
        renderLibrary(mainContent);
    });

    addRoute('/settings', (params) => {
        setState('currentView', 'settings');
        renderSettings(mainContent);
    });

    addRoute('/community', (params) => {
        setState('currentView', 'community');
        renderCommunity(mainContent);
    });

    addRoute('/help', (params) => {
        setState('currentView', 'help');
        renderHelp(mainContent);
    });

    initRouter();
}

document.addEventListener('DOMContentLoaded', renderApp);
