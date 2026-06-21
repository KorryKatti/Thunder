import {
    CheckUVInstalled,
    GetUVVersion,
    InstallUV,
    GetRepoInfo,
    GetReadme,
    DetectPythonProject,
    DownloadAndInstall,
    GetInstalledApps,
    GetAppDetail,
    GetAppSize,
    LaunchApp,
    UninstallApp,
    UpdateApp,
    CreateConfig,
    UpdateLaunchType,
    CheckForUpdates,
    GetUpdateCount,
    OpenExternal,
    GetSettings,
    UpdateSettings,
    ClearCache,
    ResetAllData,
    RepairApp
} from '../wailsjs/go/main/App';

// --- UV ---

export async function checkUV() {
    try {
        const installed = await CheckUVInstalled();
        const version = installed ? await GetUVVersion() : '';
        return { installed, version };
    } catch (e) {
        console.error('CheckUV error:', e);
        return { installed: false, version: '' };
    }
}

export async function installUV() {
    try {
        const output = await InstallUV();
        return { success: true, output };
    } catch (e) {
        console.error('InstallUV error:', e);
        return { success: false, error: String(e) };
    }
}

// --- GitHub ---

export async function fetchRepoInfo(url) {
    try {
        return await GetRepoInfo(url);
    } catch (e) {
        console.error('GetRepoInfo error:', e);
        throw e;
    }
}

export async function fetchReadme(url) {
    try {
        return await GetReadme(url);
    } catch (e) {
        console.error('GetReadme error:', e);
        return '';
    }
}

// --- Project Detection ---

export async function detectPythonProject(url) {
    try {
        return await DetectPythonProject(url);
    } catch (e) {
        console.error('DetectPythonProject error:', e);
        throw e;
    }
}

// --- Install ---

export async function downloadAndInstall(url) {
    try {
        const output = await DownloadAndInstall(url);
        return { success: true, output };
    } catch (e) {
        console.error('DownloadAndInstall error:', e);
        return { success: false, error: String(e) };
    }
}

// --- Library ---

export async function getInstalledApps() {
    try {
        return await GetInstalledApps();
    } catch (e) {
        console.error('GetInstalledApps error:', e);
        return [];
    }
}

export async function getAppDetail(dirName) {
    try {
        return await GetAppDetail(dirName);
    } catch (e) {
        console.error('GetAppDetail error:', e);
        throw e;
    }
}

export async function launchApp(dirName) {
    try {
        await LaunchApp(dirName);
        return { success: true };
    } catch (e) {
        console.error('LaunchApp error:', e);
        return { success: false, error: String(e) };
    }
}

export async function uninstallApp(dirName) {
    try {
        await UninstallApp(dirName);
        return { success: true };
    } catch (e) {
        console.error('UninstallApp error:', e);
        return { success: false, error: String(e) };
    }
}

export async function getAppSize(dirName) {
    try {
        return await GetAppSize(dirName);
    } catch (e) {
        return '?';
    }
}

export async function updateApp(dirName) {
    try {
        const output = await UpdateApp(dirName);
        return { success: true, output };
    } catch (e) {
        console.error('UpdateApp error:', e);
        return { success: false, error: String(e) };
    }
}

export async function repairApp(dirName) {
    try {
        const output = await RepairApp(dirName);
        return { success: true, output };
    } catch (e) {
        console.error('RepairApp error:', e);
        return { success: false, error: String(e) };
    }
}

export async function createConfig(dirName) {
    try {
        await CreateConfig(dirName);
        return { success: true };
    } catch (e) {
        console.error('CreateConfig error:', e);
        return { success: false, error: String(e) };
    }
}

export async function updateLaunchType(dirName, launchType) {
    try {
        await UpdateLaunchType(dirName, launchType);
        return { success: true };
    } catch (e) {
        console.error('UpdateLaunchType error:', e);
        return { success: false, error: String(e) };
    }
}

// --- Updates ---

export async function checkForUpdates() {
    try {
        return await CheckForUpdates();
    } catch (e) {
        console.error('CheckForUpdates error:', e);
        return [];
    }
}

export async function getUpdateCount() {
    try {
        return await GetUpdateCount();
    } catch (e) {
        console.error('GetUpdateCount error:', e);
        return 0;
    }
}

// --- External ---

export async function openExternal(url) {
    try {
        await OpenExternal(url);
    } catch (e) {
        console.error('OpenExternal error:', e);
    }
}

// --- Settings ---

export async function getSettings() {
    try {
        return await GetSettings();
    } catch (e) {
        console.error('GetSettings error:', e);
        return { github_token: '', install_dir: '', python_path: '' };
    }
}

export async function updateSettings(gitHubToken, installDir, pythonPath) {
    try {
        await UpdateSettings(gitHubToken, installDir, pythonPath);
        return { success: true };
    } catch (e) {
        console.error('UpdateSettings error:', e);
        return { success: false, error: String(e) };
    }
}

export async function clearCache() {
    try {
        await ClearCache();
        return { success: true };
    } catch (e) {
        console.error('ClearCache error:', e);
        return { success: false, error: String(e) };
    }
}

export async function resetAllData() {
    try {
        await ResetAllData();
        return { success: true };
    } catch (e) {
        console.error('ResetAllData error:', e);
        return { success: false, error: String(e) };
    }
}

// --- Progress Events ---

export function onInstallProgress(callback) {
    if (window.runtime && window.runtime.EventsOn) {
        window.runtime.EventsOn('install-progress', callback);
    }
}

export function offInstallProgress() {
    if (window.runtime && window.runtime.EventsOff) {
        window.runtime.EventsOff('install-progress');
    }
}

// --- Avatars ---

export function getAvatarUrl(url) {
    try {
        const match = url.match(/github\.com\/([^/]+)/);
        if (match) {
            return `https://github.com/${match[1]}.png`;
        }
    } catch (e) {}
    return '';
}
