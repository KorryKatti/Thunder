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
)

// App struct
type App struct {
	ctx         context.Context
	installBase string // ~/.thunder-nightly
}

// IndexEntry represents one app in index.json
type IndexEntry struct {
	Name        string `json:"name"`
	FullName    string `json:"full_name"`
	Repo        string `json:"repo"`
	URL         string `json:"url"`
	DirName     string `json:"dir_name"`
	EntryPoint  string `json:"entry_point"`
	Description string `json:"description"`
	InstalledAt string `json:"installed_at"`
}

// ProjectInfo holds detected project metadata
type ProjectInfo struct {
	HasPyproject   bool   `json:"has_pyproject"`
	HasRequirements bool  `json:"has_requirements"`
	ProjectName    string `json:"project_name"`
	EntryPoint     string `json:"entry_point"`
	Language       string `json:"language"`
	FileName       string `json:"file_name"` // pyproject.toml or requirements.txt
	FileSize       int64  `json:"file_size"`
}

// RepoInfo holds GitHub repository metadata
type RepoInfo struct {
	Name          string
	FullName      string
	Description   string
	Stars         int
	Forks         int
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
	Language        string       `json:"language"`
	License         *RepoLicense `json:"license"`
	HTMLURL         string       `json:"html_url"`
	DefaultBranch   string       `json:"default_branch"`
}

// NewApp creates a new App application struct
func NewApp() *App {
	home, _ := os.UserHomeDir()
	installBase := filepath.Join(home, ".thunder-nightly")

	os.MkdirAll(filepath.Join(installBase, "downloading"), 0755)
	os.MkdirAll(filepath.Join(installBase, "apps"), 0755)

	return &App{installBase: installBase}
}

// startup is called when the app starts
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
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

	patterns := []*regexp.Regexp{
		regexp.MustCompile(`github\.com/([^/]+)/([^/]+)`),
		regexp.MustCompile(`^([^/]+)/([^/]+)$`),
	}

	for _, p := range patterns {
		matches := p.FindStringSubmatch(url)
		if matches != nil {
			return matches[1], matches[2], nil
		}
	}
	return "", "", fmt.Errorf("invalid GitHub URL: %s", url)
}

func (a *App) GetRepoInfo(url string) (*RepoInfo, error) {
	log.Printf("GetRepoInfo called with URL: %s", url)
	owner, repo, err := parseGitHubURL(url)
	if err != nil {
		return nil, err
	}
	log.Printf("Parsed owner=%s repo=%s", owner, repo)

	apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s", owner, repo)
	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept", "application/vnd.github.v3+json")
	req.Header.Set("User-Agent", "thunder-nightly")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch repo: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 404 {
		return nil, fmt.Errorf("repository not found: %s/%s", owner, repo)
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
	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Accept", "application/vnd.github.v3.raw")
	req.Header.Set("User-Agent", "thunder-nightly")

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
	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept", "application/vnd.github.v3+json")
	req.Header.Set("User-Agent", "thunder-nightly")

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

// --- Download & Install ---

func (a *App) DownloadAndInstall(url string) (string, error) {
	log.Printf("DownloadAndInstall: %s", url)

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

	// 2. Download zip
	downloadDir := filepath.Join(a.installBase, "downloading")
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

	written, err := io.Copy(out, resp.Body)
	if err != nil {
		return "", err
	}
	log.Printf("Downloaded %d bytes", written)

	// 3. Extract zip
	appDir := filepath.Join(a.installBase, "apps", repo)
	os.RemoveAll(appDir) // clean previous if exists
	os.MkdirAll(appDir, 0755)

	err = extractZip(zipPath, appDir)
	if err != nil {
		return "", fmt.Errorf("extract failed: %w", err)
	}

	// GitHub zip extracts to repo-branch/, move contents up
	entries, _ := os.ReadDir(appDir)
	if len(entries) == 1 && entries[0].IsDir() {
		subDir := filepath.Join(appDir, entries[0].Name())
		// Move contents from subDir to appDir
		moveContents(subDir, appDir)
		os.RemoveAll(subDir)
	}

	// 4. Clean download
	os.Remove(zipPath)

	// 5. Detect project and create venv
	projectInfo, err := a.DetectPythonProject(url)
	if err != nil {
		log.Printf("Warning: could not detect project: %v", err)
	}

	// Create venv with uv
	log.Printf("Creating venv in %s", appDir)
	venvCmd := exec.Command("uv", "venv", filepath.Join(appDir, "venv"))
	venvOutput, err := venvCmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("venv creation failed: %s: %w", string(venvOutput), err)
	}
	log.Printf("Venv created: %s", string(venvOutput))

	// Install dependencies
	if projectInfo != nil {
		if projectInfo.HasPyproject {
			log.Printf("Installing with uv sync")
			syncCmd := exec.Command("uv", "sync", "--directory", appDir)
			syncOutput, err := syncCmd.CombinedOutput()
			if err != nil {
				log.Printf("uv sync warning: %s", string(syncOutput))
			}
		} else if projectInfo.HasRequirements {
			log.Printf("Installing from %s", projectInfo.FileName)
			reqPath := filepath.Join(appDir, projectInfo.FileName)
			pipCmd := exec.Command(
				filepath.Join(appDir, "venv", "bin", "pip"),
				"install", "-r", reqPath,
			)
			pipOutput, err := pipCmd.CombinedOutput()
			if err != nil {
				log.Printf("pip install warning: %s", string(pipOutput))
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
	configData, _ := json.MarshalIndent(config, "", "  ")
	os.WriteFile(filepath.Join(appDir, ".thunder.json"), configData, 0644)

	// 7. Update index
	now := fmt.Sprintf("%d", os.Getpid()) // placeholder timestamp
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
	a.saveIndex(index)

	log.Printf("Install complete: %s", repoInfo.Name)
	return fmt.Sprintf("Successfully installed %s", repoInfo.Name), nil
}

// --- Library ---

func (a *App) GetInstalledApps() []IndexEntry {
	return a.loadIndex()
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
	venvPython := filepath.Join(appDir, "venv", "bin", "python")
	if _, err := os.Stat(venvPython); err == nil {
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

	entryPoint, _ := config["entry_point"].(string)

	pythonPath := filepath.Join(appDir, "venv", "bin", "python")
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

		// Update config with corrected entry point
		config["entry_point"] = found
		configData, _ := json.MarshalIndent(config, "", "  ")
		os.WriteFile(configPath, configData, 0644)
	}

	// Check if venv python exists
	if _, err := os.Stat(pythonPath); err != nil {
		return fmt.Errorf("venv python not found: %s — try reinstalling", pythonPath)
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
		return launchInTerminal(pythonPath, mainScript, appDir)
	}

	// Launch GUI app directly
	cmd := exec.Command(pythonPath, mainScript)
	cmd.Dir = appDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin

	return cmd.Start()
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

		// Fallback: launch directly
		cmd := exec.Command(pythonPath, "-u", scriptPath)
		cmd.Dir = workDir
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.Stdin = os.Stdin
		return cmd.Start()
	}
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
	a.saveIndex(updated)

	return nil
}

// --- Updates ---

func (a *App) CheckForUpdates() []map[string]string {
	index := a.loadIndex()
	var updates []map[string]string

	for _, entry := range index {
		appDir := filepath.Join(a.installBase, "apps", entry.DirName)

		// Git fetch to check for updates
		fetchCmd := exec.Command("git", "-C", appDir, "fetch", "origin")
		fetchCmd.Run() // ignore errors (not a git repo, network, etc.)

		// Check if behind
		statusCmd := exec.Command("git", "-C", appDir, "rev-list", "--count", "HEAD..@{u}")
		out, err := statusCmd.Output()
		if err != nil {
			continue
		}

		count := strings.TrimSpace(string(out))
		if count != "0" && count != "" {
			updates = append(updates, map[string]string{
				"dir_name": entry.DirName,
				"name":     entry.Name,
				"commits":  count,
			})
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
	venvPython := filepath.Join(appDir, "venv", "bin", "python")
	if out, err := exec.Command(venvPython, "--version").Output(); err == nil {
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

// --- Helpers ---

func extractZip(src, dest string) error {
	r, err := zip.OpenReader(src)
	if err != nil {
		return err
	}
	defer r.Close()

	for _, f := range r.File {
		fpath := filepath.Join(dest, f.Name)

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

func moveContents(src, dest string) {
	entries, _ := os.ReadDir(src)
	for _, entry := range entries {
		srcPath := filepath.Join(src, entry.Name())
		destPath := filepath.Join(dest, entry.Name())
		os.Rename(srcPath, destPath)
	}
}
