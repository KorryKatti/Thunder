package main

import (
	"archive/zip"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"time"

	wailsRuntime "github.com/wailsapp/wails/v2/pkg/runtime"
)

// Compiled regex patterns for GitHub URL parsing
var (
	githubPattern = regexp.MustCompile(`github\.com/([^/]+)/([^/]+)`)
	ownerRepoPattern = regexp.MustCompile(`^([^/]+)/([^/]+)$`)
)

// App struct
type App struct {
	ctx         context.Context
	installBase string // ~/.thunder-nightly
	settings    *Settings
}

// Settings holds user-configurable preferences
type Settings struct {
	GitHubToken string `json:"github_token"`
	InstallDir  string `json:"install_dir"`
	PythonPath  string `json:"python_path"`
}

// IndexEntry represents one app in index.json
type IndexEntry struct {
	Name         string  `json:"name"`
	FullName     string  `json:"full_name"`
	Repo         string  `json:"repo"`
	URL          string  `json:"url"`
	DirName      string  `json:"dir_name"`
	EntryPoint   string  `json:"entry_point"`
	Description  string  `json:"description"`
	InstalledAt  string  `json:"installed_at"`
	LaunchCount  float64 `json:"launch_count"`
	LastLaunched string  `json:"last_launched"`
}

// ProjectInfo holds detected project metadata
type ProjectInfo struct {
	HasPyproject    bool   `json:"has_pyproject"`
	HasRequirements bool   `json:"has_requirements"`
	ProjectName     string `json:"project_name"`
	EntryPoint      string `json:"entry_point"`
	ScriptName      string `json:"script_name"`
	Language        string `json:"language"`
	FileName        string `json:"file_name"` // pyproject.toml or requirements.txt
	FileSize        int64  `json:"file_size"`
}

// RepoInfo holds GitHub repository metadata
type RepoInfo struct {
	Name          string
	FullName      string
	Description   string
	Stars         int
	Forks         int
	Size          int
	Language      string
	LicenseName   string
	URL           string
	DefaultBranch string
}

// RepoLicense holds license info
type RepoLicense struct {
	Name string `json:"name"`
}

// GitHubRepo is the raw API response
type GitHubRepo struct {
	Name            string       `json:"name"`
	FullName        string       `json:"full_name"`
	Description     string       `json:"description"`
	StargazersCount int          `json:"stargazers_count"`
	ForksCount      int          `json:"forks_count"`
	Size            int          `json:"size"`
	Language        string       `json:"language"`
	License         *RepoLicense `json:"license"`
	HTMLURL         string       `json:"html_url"`
	DefaultBranch   string       `json:"default_branch"`
}

// GitHubCommit is used for update checking
type GitHubCommit struct {
	SHA string `json:"sha"`
}

// NewApp creates a new App application struct
func NewApp() *App {
	home, err := os.UserHomeDir()
	if err != nil {
		log.Printf("Warning: could not get home dir: %v, using current dir", err)
		home = "."
	}
	installBase := filepath.Join(home, ".thunder-nightly")

	if err := os.MkdirAll(filepath.Join(installBase, "downloading"), 0755); err != nil {
		log.Printf("Warning: could not create downloading dir: %v", err)
	}
	if err := os.MkdirAll(filepath.Join(installBase, "apps"), 0755); err != nil {
		log.Printf("Warning: could not create apps dir: %v", err)
	}

	app := &App{installBase: installBase}
	app.loadSettings()
	return app
}

// startup is called when the app starts
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// emitProgress sends a progress event to the frontend
func (a *App) emitProgress(step, message string) {
	wailsRuntime.EventsEmit(a.ctx, "install-progress", map[string]string{
		"step":    step,
		"message": message,
	})
}

func (a *App) emitDownloadProgress(downloaded, total int64) {
	pct := 0
	if total > 0 {
		pct = int(float64(downloaded) / float64(total) * 100)
	}
	wailsRuntime.EventsEmit(a.ctx, "install-progress", map[string]string{
		"step":       "download",
		"message":    fmt.Sprintf("Downloading... %d%%", pct),
		"downloaded": fmt.Sprintf("%d", downloaded),
		"total":      fmt.Sprintf("%d", total),
		"percent":    fmt.Sprintf("%d", pct),
	})
}

// --- Settings Management ---

func (a *App) loadSettings() {
	settingsPath := filepath.Join(a.installBase, "settings.json")
	data, err := os.ReadFile(settingsPath)
	if err != nil {
		a.settings = &Settings{}
		return
	}
	var s Settings
	if err := json.Unmarshal(data, &s); err != nil {
		a.settings = &Settings{}
		return
	}
	a.settings = &s
}

func (a *App) saveSettings() error {
	settingsPath := filepath.Join(a.installBase, "settings.json")
	data, err := json.MarshalIndent(a.settings, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(settingsPath, data, 0644)
}

func (a *App) GetSettings() *Settings {
	return a.settings
}

func (a *App) UpdateSettings(gitHubToken, installDir, pythonPath string) error {
	if gitHubToken != "" {
		a.settings.GitHubToken = gitHubToken
	}
	if installDir != "" {
		a.settings.InstallDir = installDir
	}
	if pythonPath != "" {
		a.settings.PythonPath = pythonPath
	}
	return a.saveSettings()
}

func (a *App) ClearCache() error {
	downloadDir := filepath.Join(a.installBase, "downloading")
	entries, err := os.ReadDir(downloadDir)
	if err != nil {
		return err
	}
	for _, e := range entries {
		os.Remove(filepath.Join(downloadDir, e.Name()))
	}
	return nil
}

func (a *App) ResetAllData() error {
	return os.RemoveAll(a.installBase)
}

// --- Index Management ---

func (a *App) loadIndex() []IndexEntry {
	indexPath := filepath.Join(a.installBase, "index.json")
	data, err := os.ReadFile(indexPath)
	if err != nil {
		return []IndexEntry{}
	}
	var entries []IndexEntry
	json.Unmarshal(data, &entries)
	return entries
}

func (a *App) saveIndex(entries []IndexEntry) error {
	indexPath := filepath.Join(a.installBase, "index.json")
	data, err := json.MarshalIndent(entries, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(indexPath, data, 0644)
}

// --- GitHub API ---

func parseGitHubURL(url string) (owner, repo string, err error) {
	url = strings.TrimSpace(url)
	url = strings.TrimSuffix(url, "/")
	url = strings.TrimSuffix(url, ".git")

	if matches := githubPattern.FindStringSubmatch(url); matches != nil {
		return matches[1], matches[2], nil
	}
	if matches := ownerRepoPattern.FindStringSubmatch(url); matches != nil {
		return matches[1], matches[2], nil
	}
	return "", "", fmt.Errorf("invalid GitHub URL: %s", url)
}

func (a *App) newGitHubRequest(apiURL string) (*http.Request, error) {
	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept", "application/vnd.github.v3+json")
	req.Header.Set("User-Agent", "thunder-nightly")
	if a.settings != nil && a.settings.GitHubToken != "" {
		req.Header.Set("Authorization", "token "+a.settings.GitHubToken)
	}
	return req, nil
}

func (a *App) GetRepoInfo(url string) (*RepoInfo, error) {
	log.Printf("GetRepoInfo called with URL: %s", url)
	owner, repo, err := parseGitHubURL(url)
	if err != nil {
		return nil, err
	}
	log.Printf("Parsed owner=%s repo=%s", owner, repo)

	apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s", owner, repo)
	req, err := a.newGitHubRequest(apiURL)
	if err != nil {
		return nil, err
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch repo: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 404 {
		return nil, fmt.Errorf("repository not found: %s/%s", owner, repo)
	}
	if resp.StatusCode == 403 {
		return nil, fmt.Errorf("GitHub API rate limit exceeded — add a token in Settings")
	}
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("GitHub API error: %d", resp.StatusCode)
	}

	var ghRepo GitHubRepo
	if err := json.NewDecoder(resp.Body).Decode(&ghRepo); err != nil {
		return nil, err
	}

	licenseName := ""
	if ghRepo.License != nil {
		licenseName = ghRepo.License.Name
	}

	return &RepoInfo{
		Name:          ghRepo.Name,
		FullName:      ghRepo.FullName,
		Description:   ghRepo.Description,
		Stars:         ghRepo.StargazersCount,
		Forks:         ghRepo.ForksCount,
		Size:          ghRepo.Size,
		Language:      ghRepo.Language,
		LicenseName:   licenseName,
		URL:           ghRepo.HTMLURL,
		DefaultBranch: ghRepo.DefaultBranch,
	}, nil
}

func (a *App) GetReadme(url string) (string, error) {
	owner, repo, err := parseGitHubURL(url)
	if err != nil {
		return "", err
	}

	apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s/readme", owner, repo)
	req, err := a.newGitHubRequest(apiURL)
	if err != nil {
		return "", err
	}
	req.Header.Set("Accept", "application/vnd.github.v3.raw")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("README not found (status %d)", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return string(body), nil
}

// --- Python Project Detection ---

func (a *App) fetchFileList(owner, repo, branch string) ([]map[string]interface{}, error) {
	apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s/git/trees/%s?recursive=1", owner, repo, branch)
	req, err := a.newGitHubRequest(apiURL)
	if err != nil {
		return nil, err
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("failed to fetch tree: %d", resp.StatusCode)
	}

	var tree struct {
		Tree []map[string]interface{} `json:"tree"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&tree); err != nil {
		return nil, err
	}
	return tree.Tree, nil
}

func (a *App) DetectPythonProject(url string) (*ProjectInfo, error) {
	log.Printf("DetectPythonProject: %s", url)
	owner, repo, err := parseGitHubURL(url)
	if err != nil {
		return nil, err
	}

	repoInfo, err := a.GetRepoInfo(url)
	if err != nil {
		return nil, err
	}

	tree, err := a.fetchFileList(owner, repo, repoInfo.DefaultBranch)
	if err != nil {
		return nil, err
	}

	info := &ProjectInfo{
		ProjectName: repoInfo.Name,
		Language:    repoInfo.Language,
	}

	// Collect all Python files for entry point detection
	var pyFiles []string
	var pySizes map[string]int64 = make(map[string]int64)

	// Search for project files in priority order
	searchFiles := []string{
		"pyproject.toml",
		"setup.py",
		"setup.cfg",
		"requirements.txt",
		"Pipfile",
	}

	for _, node := range tree {
		path, _ := node["path"].(string)
		size, _ := node["size"].(float64)
		base := filepath.Base(path)
		nodeType, _ := node["type"].(string)

		if nodeType != "blob" {
			continue
		}

		// Collect .py files (root or one level deep)
		if strings.HasSuffix(base, ".py") {
			parts := strings.Split(path, "/")
			if len(parts) <= 2 {
				pyFiles = append(pyFiles, path)
				pySizes[path] = int64(size)
			}
		}

		// Only match config files in root or one level deep
		parts := strings.Split(path, "/")
		if len(parts) > 2 {
			continue
		}

		for _, sf := range searchFiles {
			if base == sf {
				switch sf {
				case "pyproject.toml":
					info.HasPyproject = true
					info.FileName = path
					info.FileSize = int64(size)
				case "requirements.txt":
					if !info.HasPyproject {
						info.HasRequirements = true
						info.FileName = path
						info.FileSize = int64(size)
					}
				case "setup.py", "setup.cfg", "Pipfile":
					if !info.HasPyproject && !info.HasRequirements {
						info.HasRequirements = true
						info.FileName = path
						info.FileSize = int64(size)
					}
				}
			}
		}
	}

	// Detect entry point from collected Python files
	info.EntryPoint = detectEntryPoint(pyFiles, pySizes)

	// Don't error if no project file found — some projects use only built-in libs
	if info.FileName == "" {
		info.FileName = "(none — using built-in libraries)"
		log.Printf("No project file found, using built-in libs. Entry: %s", info.EntryPoint)
	} else {
		log.Printf("Detected project: %s, file: %s, entry: %s", info.ProjectName, info.FileName, info.EntryPoint)
	}

	return info, nil
}

func detectEntryPoint(pyFiles []string, pySizes map[string]int64) string {
	if len(pyFiles) == 0 {
		return "main.py"
	}

	// Priority names in order of preference
	priority := []string{
		"__main__.py",
		"main.py",
		"app.py",
		"cli.py",
		"run.py",
		"start.py",
		"launcher.py",
		"gui.py",
		"window.py",
	}

	// First pass: exact name match at root level
	for _, name := range priority {
		for _, f := range pyFiles {
			if filepath.Base(f) == name && !strings.Contains(f, "/") {
				return f
			}
		}
	}

	// Second pass: name match one level deep
	for _, name := range priority {
		for _, f := range pyFiles {
			if filepath.Base(f) == name {
				return f
			}
		}
	}

	// Third pass: largest .py file at root (likely the main one)
	var bestFile string
	var bestSize int64
	for _, f := range pyFiles {
		if !strings.Contains(f, "/") {
			s := pySizes[f]
			if s > bestSize {
				bestSize = s
				bestFile = f
			}
		}
	}
	if bestFile != "" {
		return bestFile
	}

	// Fourth pass: any .py file
	if len(pyFiles) > 0 {
		return pyFiles[0]
	}

	return "main.py"
}

// --- Helpers ---

// venvBinDir returns the platform-appropriate bin/Scripts directory inside a venv
func venvBinDir(venvPath string) string {
	if runtime.GOOS == "windows" {
		return filepath.Join(venvPath, "Scripts")
	}
	return filepath.Join(venvPath, "bin")
}

// venvPython returns the path to the Python executable in a venv
func venvPython(venvPath string) string {
	python := "python"
	if runtime.GOOS == "windows" {
		python = "python.exe"
	}
	return filepath.Join(venvBinDir(venvPath), python)
}

// venvPip returns the path to pip in a venv
func venvPip(venvPath string) string {
	pip := "pip"
	if runtime.GOOS == "windows" {
		pip = "pip.exe"
	}
	return filepath.Join(venvBinDir(venvPath), pip)
}

// parseScriptName extracts the first script name from [project.scripts] in pyproject.toml
func parseScriptName(pyprojectPath string) string {
	data, err := os.ReadFile(pyprojectPath)
	if err != nil {
		return ""
	}
	content := string(data)

	// Find [project.scripts] section
	idx := strings.Index(content, "[project.scripts]")
	if idx == -1 {
		return ""
	}
	section := content[idx:]

	// Read lines until next section or end
	lines := strings.Split(section, "\n")
	for _, line := range lines[1:] {
		trimmed := strings.TrimSpace(line)
		if trimmed == "" {
			continue
		}
		// New section means we're done
		if strings.HasPrefix(trimmed, "[") {
			break
		}
		// Parse "script_name = "module.path:function""
		if eqIdx := strings.Index(trimmed, "="); eqIdx > 0 {
			scriptName := strings.TrimSpace(trimmed[:eqIdx])
			if scriptName != "" {
				return scriptName
			}
		}
	}
	return ""
}

// --- Download & Install ---

func (a *App) DownloadAndInstall(url string) (string, error) {
	log.Printf("DownloadAndInstall: %s", url)

	a.emitProgress("info", "Fetching repository info...")

	owner, repo, err := parseGitHubURL(url)
	if err != nil {
		return "", err
	}

	repoInfo, err := a.GetRepoInfo(url)
	if err != nil {
		return "", err
	}

	// 1. Check if already installed
	index := a.loadIndex()
	for _, entry := range index {
		if entry.Repo == fmt.Sprintf("%s/%s", owner, repo) {
			return "", fmt.Errorf("already installed: %s", entry.Name)
		}
	}

	a.emitProgress("download", "Downloading repository...")

	// 2. Download zip
	downloadDir := filepath.Join(a.installBase, "downloading")
	if err := os.MkdirAll(downloadDir, 0755); err != nil {
		return "", fmt.Errorf("failed to create download dir: %w", err)
	}
	zipPath := filepath.Join(downloadDir, repo+".zip")

	zipURL := fmt.Sprintf("https://github.com/%s/%s/archive/refs/heads/%s.zip", owner, repo, repoInfo.DefaultBranch)
	log.Printf("Downloading from: %s", zipURL)

	resp, err := http.Get(zipURL)
	if err != nil {
		return "", fmt.Errorf("download failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("download failed: HTTP %d", resp.StatusCode)
	}

	out, err := os.Create(zipPath)
	if err != nil {
		return "", err
	}
	defer out.Close()

	totalSize := resp.ContentLength
	var downloaded int64
	buf := make([]byte, 32*1024)
	for {
		n, readErr := resp.Body.Read(buf)
		if n > 0 {
			_, writeErr := out.Write(buf[:n])
			if writeErr != nil {
				return "", writeErr
			}
			downloaded += int64(n)
			a.emitDownloadProgress(downloaded, totalSize)
		}
		if readErr != nil {
			break
		}
	}
	log.Printf("Downloaded %d bytes", downloaded)

	a.emitProgress("extract", "Extracting files...")

	// 3. Extract zip
	appDir := filepath.Join(a.installBase, "apps", repo)
	if err := os.RemoveAll(appDir); err != nil {
		return "", fmt.Errorf("failed to clean previous install: %w", err)
	}
	if err := os.MkdirAll(appDir, 0755); err != nil {
		return "", fmt.Errorf("failed to create app dir: %w", err)
	}

	err = extractZip(zipPath, appDir)
	if err != nil {
		return "", fmt.Errorf("extract failed: %w", err)
	}

	// GitHub zip extracts to repo-branch/, move contents up
	entries, err := os.ReadDir(appDir)
	if err != nil {
		return "", fmt.Errorf("failed to read extracted dir: %w", err)
	}
	if len(entries) == 1 && entries[0].IsDir() {
		subDir := filepath.Join(appDir, entries[0].Name())
		if err := moveContents(subDir, appDir); err != nil {
			return "", fmt.Errorf("failed to move extracted contents: %w", err)
		}
		os.RemoveAll(subDir)
	}

	// 4. Clean download
	os.Remove(zipPath)

	a.emitProgress("detect", "Detecting project type...")

	// 5. Detect project and create venv
	projectInfo, err := a.DetectPythonProject(url)
	if err != nil {
		log.Printf("Warning: could not detect project: %v", err)
	}

	// Parse script name from local pyproject.toml after extract
	if projectInfo != nil && projectInfo.HasPyproject {
		pyprojectPath := filepath.Join(appDir, projectInfo.FileName)
		if scriptName := parseScriptName(pyprojectPath); scriptName != "" {
			projectInfo.ScriptName = scriptName
			log.Printf("Found script entry point: %s", scriptName)
		}
	}

	venvPath := filepath.Join(appDir, "venv")

	a.emitProgress("venv", "Creating virtual environment...")

	// Create venv with uv
	log.Printf("Creating venv in %s", appDir)
	venvCmd := exec.Command("uv", "venv", venvPath)
	venvOutput, err := venvCmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("venv creation failed: %s: %w", string(venvOutput), err)
	}
	log.Printf("Venv created: %s", string(venvOutput))

	a.emitProgress("deps", "Installing dependencies...")

	// Install dependencies
	if projectInfo != nil {
		installed := false

		if projectInfo.HasPyproject {
			log.Printf("Installing with uv sync")
			syncCmd := exec.Command("uv", "sync", "--directory", appDir)
			syncCmd.Env = append(os.Environ(), "UV_PROJECT_ENVIRONMENT="+venvPath)
			syncOutput, err := syncCmd.CombinedOutput()
			if err != nil {
				log.Printf("uv sync failed: %s, trying fallback", string(syncOutput))
			} else {
				installed = true
			}
		}

		// Fallback: try uv pip install if sync didn't work or wasn't applicable
		if !installed {
			reqPath := filepath.Join(appDir, projectInfo.FileName)
			if _, err := os.Stat(reqPath); err == nil {
				log.Printf("Installing from %s via uv pip", projectInfo.FileName)
				pipCmd := exec.Command("uv", "pip", "install", "--python", venvPython(venvPath), "-r", reqPath)
				pipOutput, err := pipCmd.CombinedOutput()
				if err != nil {
					log.Printf("uv pip install failed: %s", string(pipOutput))
				} else {
					installed = true
				}
			}
		}

		// Last fallback: try editable install
		if !installed && projectInfo.HasPyproject {
			log.Printf("Trying uv pip install -e .")
			editCmd := exec.Command("uv", "pip", "install", "--python", venvPython(venvPath), "-e", appDir)
			editOutput, err := editCmd.CombinedOutput()
			if err != nil {
				log.Printf("uv pip install -e failed: %s", string(editOutput))
			}
		}
	}

	// 6. Create .thunder.json config
	entryPoint := "main.py"
	if projectInfo != nil && projectInfo.EntryPoint != "" {
		entryPoint = projectInfo.EntryPoint
	}

	config := map[string]interface{}{
		"name":        repoInfo.Name,
		"repo":        fmt.Sprintf("%s/%s", owner, repo),
		"url":         url,
		"entry_point": entryPoint,
		"description": repoInfo.Description,
	}
	if projectInfo != nil && projectInfo.ScriptName != "" {
		config["script_name"] = projectInfo.ScriptName
	}
	configData, _ := json.MarshalIndent(config, "", "  ")
	if err := os.WriteFile(filepath.Join(appDir, ".thunder.json"), configData, 0644); err != nil {
		log.Printf("Warning: could not write config: %v", err)
	}

	// 7. Update index
	now := time.Now().Format(time.RFC3339)
	entry := IndexEntry{
		Name:        repoInfo.Name,
		FullName:    repoInfo.FullName,
		Repo:        fmt.Sprintf("%s/%s", owner, repo),
		URL:         url,
		DirName:     repo,
		EntryPoint:  entryPoint,
		Description: repoInfo.Description,
		InstalledAt: now,
	}
	index = append(index, entry)
	if err := a.saveIndex(index); err != nil {
		log.Printf("Warning: could not save index: %v", err)
	}

	log.Printf("Install complete: %s", repoInfo.Name)
	a.emitProgress("done", fmt.Sprintf("Successfully installed %s", repoInfo.Name))
	return fmt.Sprintf("Successfully installed %s", repoInfo.Name), nil
}

// --- Library ---

func (a *App) GetInstalledApps() []IndexEntry {
	entries := a.loadIndex()
	for i := range entries {
		configPath := filepath.Join(a.installBase, "apps", entries[i].DirName, ".thunder.json")
		data, err := os.ReadFile(configPath)
		if err != nil {
			continue
		}
		var config map[string]interface{}
		json.Unmarshal(data, &config)
		if count, ok := config["launch_count"].(float64); ok {
			entries[i].LaunchCount = count
		}
		if last, ok := config["last_launched"].(string); ok {
			entries[i].LastLaunched = last
		}
	}
	return entries
}

func (a *App) GetAppDetail(dirName string) (map[string]interface{}, error) {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	configPath := filepath.Join(appDir, ".thunder.json")

	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("app not found: %s", dirName)
	}

	var config map[string]interface{}
	json.Unmarshal(data, &config)

	// Check if venv exists
	if _, err := os.Stat(venvPython(filepath.Join(appDir, "venv"))); err == nil {
		config["venv_exists"] = true
	} else {
		config["venv_exists"] = false
	}

	return config, nil
}

func (a *App) LaunchApp(dirName string) error {
	appDir := filepath.Join(a.installBase, "apps", dirName)

	// Read config
	configPath := filepath.Join(appDir, ".thunder.json")
	data, err := os.ReadFile(configPath)
	if err != nil {
		return fmt.Errorf("app not found: %s", dirName)
	}
	var config map[string]interface{}
	json.Unmarshal(data, &config)

	// Check for script-based entry point (from [project.scripts])
	scriptName, _ := config["script_name"].(string)
	if scriptName != "" {
		return a.launchScript(appDir, scriptName, config, configPath)
	}

	// Fall back to .py file entry point
	entryPoint, _ := config["entry_point"].(string)
	pythonBin := venvPython(filepath.Join(appDir, "venv"))
	mainScript := filepath.Join(appDir, entryPoint)

	// Check if configured entry point exists, if not try to find it
	if _, err := os.Stat(mainScript); err != nil {
		log.Printf("Configured entry point %s not found, searching...", entryPoint)
		found := findLocalEntryPoint(appDir)
		if found == "" {
			return fmt.Errorf("no Python entry point found in %s", appDir)
		}
		mainScript = filepath.Join(appDir, found)
		log.Printf("Found entry point: %s", found)

		config["entry_point"] = found
		configData, _ := json.MarshalIndent(config, "", "  ")
		os.WriteFile(configPath, configData, 0644)
	}

	// Check if venv python exists
	if _, err := os.Stat(pythonBin); err != nil {
		return fmt.Errorf("venv python not found: %s — try reinstalling", pythonBin)
	}

	// Detect launch type: gui, cli, or auto
	launchType, _ := config["launch_type"].(string)
	if launchType == "" {
		launchType = "auto"
	}

	needTerminal := false
	switch launchType {
	case "cli":
		needTerminal = true
	case "gui":
		needTerminal = false
	default: // auto-detect
		needTerminal = isCLIApp(mainScript)
	}

	if needTerminal {
		preflightCheck(pythonBin, mainScript, appDir)
		a.RecordLaunch(dirName)
		return launchInTerminal(pythonBin, mainScript, appDir)
	}

	// Launch GUI app directly
	preflightCheck(pythonBin, mainScript, appDir)
	a.RecordLaunch(dirName)
	cmd := exec.Command(pythonBin, mainScript)
	cmd.Dir = appDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin

	return cmd.Start()
}

// launchScript launches an app via uv run <script-name>
func (a *App) launchScript(appDir, scriptName string, config map[string]interface{}, configPath string) error {
	venvPath := filepath.Join(appDir, "venv")

	// Detect launch type
	launchType, _ := config["launch_type"].(string)
	if launchType == "" {
		launchType = "auto"
	}

	needTerminal := false
	switch launchType {
	case "cli":
		needTerminal = true
	case "gui":
		needTerminal = false
	default:
		// For scripts, default to terminal since most [project.scripts] are CLI tools
		needTerminal = true
	}

	if needTerminal {
		return a.launchScriptInTerminal(appDir, scriptName, venvPath)
	}

	// Launch directly via uv run
	cmd := exec.Command("uv", "run", "--directory", appDir, scriptName)
	cmd.Dir = appDir
	cmd.Env = append(os.Environ(), "UV_PROJECT_ENVIRONMENT="+venvPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin

	return cmd.Start()
}

// launchScriptInTerminal launches a script in a terminal window
func (a *App) launchScriptInTerminal(appDir, scriptName, venvPath string) error {
	cmdStr := fmt.Sprintf("cd %s && UV_PROJECT_ENVIRONMENT=%s uv run %s", appDir, venvPath, scriptName)

	switch runtime.GOOS {
	case "darwin":
		cmd := exec.Command("osascript", "-e",
			fmt.Sprintf(`tell application "Terminal" to do script "%s"`, cmdStr))
		return cmd.Start()
	case "windows":
		cmd := exec.Command("cmd", "/c", "start", "cmd", "/k", cmdStr)
		return cmd.Start()
	default:
		terminals := []struct {
			bin  string
			args []string
		}{
			{"x-terminal-emulator", []string{"-e"}},
			{"gnome-terminal", []string{"--"}},
			{"konsole", []string{"-e"}},
			{"xfce4-terminal", []string{"-e"}},
			{"alacritty", []string{"-e"}},
			{"kitty", []string{}},
			{"xterm", []string{"-e"}},
			{"urxvt", []string{"-e"}},
		}

		for _, t := range terminals {
			if _, err := exec.LookPath(t.bin); err == nil {
				args := append(t.args, "sh", "-c", cmdStr)
				cmd := exec.Command(t.bin, args...)
				cmd.Dir = appDir
				return cmd.Start()
			}
		}

		return fmt.Errorf("no terminal emulator found — install one (e.g. gnome-terminal, alacritty, xterm) or set launch type to GUI")
	}
}

// preflightCheck scans the script for imports and auto-installs any missing top-level packages
func preflightCheck(pythonBin, mainScript, appDir string) {
	data, err := os.ReadFile(mainScript)
	if err != nil {
		return
	}
	content := string(data)

	// Extract import names from the first 5KB (imports are always at the top)
	if len(content) > 5096 {
		content = content[:5096]
	}

	importRe := regexp.MustCompile(`(?:^|\s)import\s+([a-zA-Z_][a-zA-Z0-9_]*)`)
	fromRe := regexp.MustCompile(`(?:^|\s)from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import`)
	seen := map[string]bool{}

	var modules []string
	for _, m := range importRe.FindAllStringSubmatch(content, -1) {
		name := m[1]
		if !seen[name] {
			seen[name] = true
			modules = append(modules, name)
		}
	}
	for _, m := range fromRe.FindAllStringSubmatch(content, -1) {
		name := m[1]
		if !seen[name] {
			seen[name] = true
			modules = append(modules, name)
		}
	}

	if len(modules) == 0 {
		return
	}

	// Check which modules are missing and install them
	var checks []string
	for _, m := range modules {
		checks = append(checks, fmt.Sprintf("try:\n    import %s\nexcept ImportError:\n    print('%s')", m, m))
	}
	pyScript := strings.Join(checks, "\n")

	checkCmd := exec.Command(pythonBin, "-c", pyScript)
	checkCmd.Dir = appDir
	out, err := checkCmd.CombinedOutput()
	if err != nil {
		return
	}

	missing := strings.Fields(strings.TrimSpace(string(out)))
	for _, pkg := range missing {
		log.Printf("Auto-installing missing module: %s", pkg)
		installCmd := exec.Command("uv", "pip", "install", "--python", pythonBin, pkg)
		installCmd.Run()
	}
}

func isCLIApp(scriptPath string) bool {
	// Read first 5KB of the file to check for GUI imports
	f, err := os.Open(scriptPath)
	if err != nil {
		return false
	}
	defer f.Close()

	buf := make([]byte, 5096)
	n, _ := f.Read(buf)
	content := string(buf[:n])

	// GUI frameworks
	guiImports := []string{
		"import tkinter", "from tkinter", "import Tk",
		"import PyQt", "from PyQt", "from PySide",
		"import pygame", "import wx",
		"import kivy", "from kivy",
		"import curses",
	}

	for _, gi := range guiImports {
		if strings.Contains(content, gi) {
			return false // has GUI imports, not CLI
		}
	}

	return true // no GUI imports found, assume CLI
}

func launchInTerminal(pythonPath, scriptPath, workDir string) error {
	switch runtime.GOOS {
	case "darwin":
		// macOS: open Terminal.app with the command
		cmd := exec.Command("osascript", "-e",
			fmt.Sprintf(`tell application "Terminal" to do script "cd %s && %s -u %s"`, workDir, pythonPath, scriptPath))
		return cmd.Start()
	case "windows":
		// Windows: use cmd /c start
		cmd := exec.Command("cmd", "/c", "start", "cmd", "/k",
			fmt.Sprintf("cd /d %s && %s -u %s", workDir, pythonPath, scriptPath))
		return cmd.Start()
	default:
		// Linux: try terminal emulators
		terminals := []struct {
			bin  string
			args []string
		}{
			{"x-terminal-emulator", []string{"-e"}},
			{"gnome-terminal", []string{"--"}},
			{"konsole", []string{"-e"}},
			{"xfce4-terminal", []string{"-e"}},
			{"alacritty", []string{"-e"}},
			{"kitty", []string{}},
			{"xterm", []string{"-e"}},
			{"urxvt", []string{"-e"}},
		}

		for _, t := range terminals {
			if _, err := exec.LookPath(t.bin); err == nil {
				args := append(t.args, pythonPath, "-u", scriptPath)
				cmd := exec.Command(t.bin, args...)
				cmd.Dir = workDir
				return cmd.Start()
			}
		}

		return fmt.Errorf("no terminal emulator found — install one (e.g. gnome-terminal, alacritty, xterm) or set launch type to GUI")
	}
}

// --- Usage Stats ---

func (a *App) RecordLaunch(dirName string) {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	configPath := filepath.Join(appDir, ".thunder.json")

	var config map[string]interface{}
	data, err := os.ReadFile(configPath)
	if err != nil {
		return
	}
	json.Unmarshal(data, &config)

	count, _ := config["launch_count"].(float64)
	config["launch_count"] = count + 1
	config["last_launched"] = time.Now().Format(time.RFC3339)

	newData, _ := json.MarshalIndent(config, "", "  ")
	os.WriteFile(configPath, newData, 0644)
}

// --- App Size ---

func (a *App) GetAppSize(dirName string) string {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	var size int64
	filepath.Walk(appDir, func(path string, info os.FileInfo, err error) error {
		if err == nil && !info.IsDir() {
			size += info.Size()
		}
		return nil
	})
	return formatSize(size)
}

func formatSize(bytes int64) string {
	if bytes < 1024 {
		return fmt.Sprintf("%d B", bytes)
	}
	if bytes < 1024*1024 {
		return fmt.Sprintf("%.1f KB", float64(bytes)/1024)
	}
	if bytes < 1024*1024*1024 {
		return fmt.Sprintf("%.1f MB", float64(bytes)/(1024*1024))
	}
	return fmt.Sprintf("%.1f GB", float64(bytes)/(1024*1024*1024))
}

// --- App Update ---

func (a *App) UpdateApp(dirName string) (string, error) {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	configPath := filepath.Join(appDir, ".thunder.json")

	data, err := os.ReadFile(configPath)
	if err != nil {
		return "", fmt.Errorf("app not found: %s", dirName)
	}

	var config map[string]interface{}
	if err := json.Unmarshal(data, &config); err != nil {
		return "", fmt.Errorf("invalid config: %w", err)
	}

	url, _ := config["url"].(string)
	if url == "" {
		return "", fmt.Errorf("no source URL stored for %s", dirName)
	}

	owner, repo, err := parseGitHubURL(url)
	if err != nil {
		return "", err
	}

	repoInfo, err := a.GetRepoInfo(url)
	if err != nil {
		return "", err
	}

	// Download latest zip
	downloadDir := filepath.Join(a.installBase, "downloading")
	os.MkdirAll(downloadDir, 0755)
	zipPath := filepath.Join(downloadDir, repo+".zip")

	zipURL := fmt.Sprintf("https://github.com/%s/%s/archive/refs/heads/%s.zip", owner, repo, repoInfo.DefaultBranch)
	resp, err := http.Get(zipURL)
	if err != nil {
		return "", fmt.Errorf("download failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("download failed: HTTP %d", resp.StatusCode)
	}

	out, err := os.Create(zipPath)
	if err != nil {
		return "", err
	}
	io.Copy(out, resp.Body)
	out.Close()

	// Preserve config and venv
	backupConfig, _ := os.ReadFile(configPath)
	venvPath := filepath.Join(appDir, "venv")
	venvBackup := filepath.Join(a.installBase, "downloading", repo+"_venv")

	// Move venv out temporarily
	os.Rename(venvPath, venvBackup)

	// Clean app dir but keep it
	entries, _ := os.ReadDir(appDir)
	for _, e := range entries {
		if e.Name() != "venv" {
			os.RemoveAll(filepath.Join(appDir, e.Name()))
		}
	}

	// Extract
	err = extractZip(zipPath, appDir)
	if err != nil {
		// Restore venv
		os.Rename(venvBackup, venvPath)
		return "", fmt.Errorf("extract failed: %w", err)
	}

	// Move contents up if needed
	extracted, _ := os.ReadDir(appDir)
	if len(extracted) == 1 && extracted[0].IsDir() && extracted[0].Name() != "venv" {
		subDir := filepath.Join(appDir, extracted[0].Name())
		moveContents(subDir, appDir)
		os.RemoveAll(subDir)
	}

	// Restore venv and config
	os.Rename(venvBackup, venvPath)
	os.WriteFile(configPath, backupConfig, 0644)
	os.Remove(zipPath)

	// Re-install dependencies
	projectInfo, _ := a.DetectPythonProject(url)
	if projectInfo != nil {
		if projectInfo.HasPyproject {
			syncCmd := exec.Command("uv", "sync", "--directory", appDir)
			syncCmd.Env = append(os.Environ(), "UV_PROJECT_ENVIRONMENT="+venvPath)
			syncCmd.CombinedOutput()
		} else if projectInfo.HasRequirements {
			reqPath := filepath.Join(appDir, projectInfo.FileName)
			if _, err := os.Stat(reqPath); err == nil {
				pipCmd := exec.Command("uv", "pip", "install", "--python", venvPython(venvPath), "-r", reqPath)
				pipCmd.CombinedOutput()
			}
		}
	}

	return fmt.Sprintf("Updated %s", config["name"]), nil
}

func findLocalEntryPoint(dir string) string {
	priority := []string{
		"__main__.py", "main.py", "app.py", "cli.py",
		"run.py", "start.py", "launcher.py", "gui.py", "window.py",
	}

	// First: exact name match at root
	for _, name := range priority {
		if _, err := os.Stat(filepath.Join(dir, name)); err == nil {
			return name
		}
	}

	// Second: find largest .py at root
	var best string
	var bestSize int64
	entries, _ := os.ReadDir(dir)
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".py") {
			info, err := e.Info()
			if err == nil && info.Size() > bestSize {
				bestSize = info.Size()
				best = e.Name()
			}
		}
	}
	if best != "" {
		return best
	}

	// Third: check one level deep
	for _, e := range entries {
		if e.IsDir() {
			subEntries, _ := os.ReadDir(filepath.Join(dir, e.Name()))
			for _, se := range subEntries {
				if !se.IsDir() && strings.HasSuffix(se.Name(), ".py") {
					for _, name := range priority {
						if se.Name() == name {
							return filepath.Join(e.Name(), se.Name())
						}
					}
				}
			}
		}
	}

	return ""
}

func (a *App) UninstallApp(dirName string) error {
	appDir := filepath.Join(a.installBase, "apps", dirName)

	// Remove directory
	if err := os.RemoveAll(appDir); err != nil {
		return fmt.Errorf("failed to remove app: %w", err)
	}

	// Update index
	index := a.loadIndex()
	var updated []IndexEntry
	for _, entry := range index {
		if entry.DirName != dirName {
			updated = append(updated, entry)
		}
	}
	if err := a.saveIndex(updated); err != nil {
		return fmt.Errorf("failed to update index: %w", err)
	}

	return nil
}

// --- Repair ---

func (a *App) RepairApp(dirName string) (string, error) {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	configPath := filepath.Join(appDir, ".thunder.json")

	data, err := os.ReadFile(configPath)
	if err != nil {
		return "", fmt.Errorf("app not found: %s", dirName)
	}

	var config map[string]interface{}
	if err := json.Unmarshal(data, &config); err != nil {
		return "", fmt.Errorf("invalid config: %w", err)
	}

	venvPath := filepath.Join(appDir, "venv")

	// Remove old venv
	os.RemoveAll(venvPath)

	// Recreate venv
	venvCmd := exec.Command("uv", "venv", venvPath)
	venvOutput, err := venvCmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("venv creation failed: %s: %w", string(venvOutput), err)
	}

	// Re-detect project info from URL
	url, _ := config["url"].(string)
	if url != "" {
		projectInfo, err := a.DetectPythonProject(url)
		if err == nil && projectInfo != nil {
			installed := false

			if projectInfo.HasPyproject {
				syncCmd := exec.Command("uv", "sync", "--directory", appDir)
				syncCmd.Env = append(os.Environ(), "UV_PROJECT_ENVIRONMENT="+venvPath)
				syncOutput, syncErr := syncCmd.CombinedOutput()
				if syncErr == nil {
					installed = true
				} else {
					log.Printf("uv sync failed during repair: %s", string(syncOutput))
				}
			}

			if !installed {
				reqPath := filepath.Join(appDir, projectInfo.FileName)
				if _, err := os.Stat(reqPath); err == nil {
					pipCmd := exec.Command("uv", "pip", "install", "--python", venvPython(venvPath), "-r", reqPath)
					pipOutput, pipErr := pipCmd.CombinedOutput()
					if pipErr == nil {
						installed = true
					} else {
						log.Printf("uv pip install failed during repair: %s", string(pipOutput))
					}
				}
			}

			if !installed && projectInfo.HasPyproject {
				editCmd := exec.Command("uv", "pip", "install", "--python", venvPython(venvPath), "-e", appDir)
				editCmd.CombinedOutput()
			}
		}
	}

	// Fix entry point
	entryPoint := findLocalEntryPoint(appDir)
	if entryPoint != "" {
		config["entry_point"] = entryPoint
	}

	newData, _ := json.MarshalIndent(config, "", "  ")
	os.WriteFile(configPath, newData, 0644)

	return fmt.Sprintf("Repaired %s", config["name"]), nil
}

// --- Updates ---

func (a *App) CheckForUpdates() []map[string]string {
	index := a.loadIndex()
	var updates []map[string]string

	for _, entry := range index {
		owner, repo, err := parseGitHubURL(entry.URL)
		if err != nil {
			continue
		}

		// Get latest commit SHA from GitHub API
		apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s/commits?sha=HEAD&per_page=1", owner, repo)
		req, err := a.newGitHubRequest(apiURL)
		if err != nil {
			continue
		}

		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			continue
		}

		if resp.StatusCode != 200 {
			resp.Body.Close()
			continue
		}

		var commits []GitHubCommit
		if err := json.NewDecoder(resp.Body).Decode(&commits); err != nil {
			resp.Body.Close()
			continue
		}
		resp.Body.Close()

		if len(commits) == 0 {
			continue
		}

		// Read the stored config to check the last known commit (if available)
		appDir := filepath.Join(a.installBase, "apps", entry.DirName)
		configPath := filepath.Join(appDir, ".thunder.json")
		configData, err := os.ReadFile(configPath)
		if err != nil {
			// Can't check — no config stored, flag as potentially updatable
			updates = append(updates, map[string]string{
				"dir_name": entry.DirName,
				"name":     entry.Name,
				"commits":  "unknown",
			})
			continue
		}

		var config map[string]interface{}
		json.Unmarshal(configData, &config)

		lastSHA, _ := config["last_commit_sha"].(string)
		latestSHA := commits[0].SHA

		if lastSHA == "" || lastSHA != latestSHA {
			updates = append(updates, map[string]string{
				"dir_name": entry.DirName,
				"name":     entry.Name,
				"commits":  "available",
			})

			// Store the latest SHA for future comparisons
			config["last_commit_sha"] = latestSHA
			newData, _ := json.MarshalIndent(config, "", "  ")
			os.WriteFile(configPath, newData, 0644)
		}
	}

	return updates
}

func (a *App) GetUpdateCount() int {
	updates := a.CheckForUpdates()
	return len(updates)
}

func (a *App) CreateConfig(dirName string) error {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	configPath := filepath.Join(appDir, ".thunder.json")

	// Read existing config or create default
	var config map[string]interface{}
	data, err := os.ReadFile(configPath)
	if err == nil {
		json.Unmarshal(data, &config)
	} else {
		config = make(map[string]interface{})
	}

	// Auto-detect entry point
	entryPoint := findLocalEntryPoint(appDir)
	if entryPoint != "" {
		config["entry_point"] = entryPoint
	}

	// Auto-detect Python version
	pythonBin := venvPython(filepath.Join(appDir, "venv"))
	if out, err := exec.Command(pythonBin, "--version").Output(); err == nil {
		config["python_version"] = strings.TrimSpace(string(out))
	}

	configData, _ := json.MarshalIndent(config, "", "  ")
	return os.WriteFile(configPath, configData, 0644)
}

func (a *App) UpdateLaunchType(dirName string, launchType string) error {
	appDir := filepath.Join(a.installBase, "apps", dirName)
	configPath := filepath.Join(appDir, ".thunder.json")

	var config map[string]interface{}
	data, err := os.ReadFile(configPath)
	if err == nil {
		json.Unmarshal(data, &config)
	} else {
		config = make(map[string]interface{})
	}

	config["launch_type"] = launchType

	configData, _ := json.MarshalIndent(config, "", "  ")
	return os.WriteFile(configPath, configData, 0644)
}

// --- UV Check ---

func (a *App) CheckUVInstalled() bool {
	_, err := exec.LookPath("uv")
	return err == nil
}

func (a *App) GetUVVersion() string {
	out, err := exec.Command("uv", "--version").Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

func (a *App) InstallUV() (string, error) {
	out, err := exec.Command("sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh").CombinedOutput()
	if err != nil {
		return string(out), fmt.Errorf("uv install failed: %w", err)
	}
	return string(out), nil
}

// --- External ---

func (a *App) OpenExternal(url string) error {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "darwin":
		cmd = exec.Command("open", url)
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}
	return cmd.Start()
}

// --- Zip Extraction ---

func extractZip(src, dest string) error {
	r, err := zip.OpenReader(src)
	if err != nil {
		return err
	}
	defer r.Close()

	dest, err = filepath.Abs(dest)
	if err != nil {
		return err
	}

	for _, f := range r.File {
		fpath := filepath.Join(dest, f.Name)

		// Zip slip protection: ensure extracted path stays within dest
		if !strings.HasPrefix(fpath, dest+string(os.PathSeparator)) && fpath != dest {
			return fmt.Errorf("illegal file path in zip: %s", f.Name)
		}

		if f.FileInfo().IsDir() {
			os.MkdirAll(fpath, 0755)
			continue
		}

		if err := os.MkdirAll(filepath.Dir(fpath), 0755); err != nil {
			return err
		}

		outFile, err := os.OpenFile(fpath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
		if err != nil {
			return err
		}

		rc, err := f.Open()
		if err != nil {
			outFile.Close()
			return err
		}

		_, err = io.Copy(outFile, rc)
		rc.Close()
		outFile.Close()
		if err != nil {
			return err
		}
	}
	return nil
}

func moveContents(src, dest string) error {
	entries, err := os.ReadDir(src)
	if err != nil {
		return fmt.Errorf("failed to read source dir: %w", err)
	}
	for _, entry := range entries {
		srcPath := filepath.Join(src, entry.Name())
		destPath := filepath.Join(dest, entry.Name())
		if err := os.Rename(srcPath, destPath); err != nil {
			return fmt.Errorf("failed to move %s: %w", entry.Name(), err)
		}
	}
	return nil
}
