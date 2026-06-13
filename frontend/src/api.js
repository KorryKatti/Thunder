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
    LaunchApp,
    UninstallApp,
    CreateConfig,
    UpdateLaunchType,
    CheckForUpdates,
    GetUpdateCount,
    OpenExternal
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
