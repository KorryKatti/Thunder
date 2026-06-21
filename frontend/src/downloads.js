const downloads = [];
const listeners = [];

export function addDownload(name, url) {
    const id = Date.now();
    const entry = { id, name, url, status: 'active', step: 'Starting...', time: new Date() };
    downloads.unshift(entry);
    notify();
    return id;
}

export function updateDownload(id, step) {
    const d = downloads.find(x => x.id === id);
    if (d) { d.step = step; notify(); }
}

export function completeDownload(id, success, error) {
    const d = downloads.find(x => x.id === id);
    if (d) {
        d.status = success ? 'done' : 'failed';
        d.step = success ? 'Complete' : error || 'Failed';
        d.time = new Date();
        notify();
    }
}

export function getDownloads() { return downloads; }

export function onDownloadsChange(fn) {
    listeners.push(fn);
    return () => { const i = listeners.indexOf(fn); if (i >= 0) listeners.splice(i, 1); };
}

function notify() { listeners.forEach(fn => fn()); }
