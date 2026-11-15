const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const path = require("path");

let backend;
const repositoryRoot = path.resolve(__dirname, "../..");
const isDevelopment = !app.isPackaged;

function requestHealth() {
  return new Promise((resolve, reject) => {
    const request = http.get("http://127.0.0.1:8000/api/health", (response) => {
      response.resume();
      response.statusCode === 200 ? resolve() : reject(new Error(`API returned ${response.statusCode}`));
    });
    request.on("error", reject);
    request.setTimeout(500, () => request.destroy(new Error("API health check timed out")));
  });
}

async function waitForBackend() {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try { await requestHealth(); return; } catch { await new Promise((resolve) => setTimeout(resolve, 250)); }
  }
  throw new Error("HEPHAESTUS local backend did not become ready within 15 seconds.");
}

function startBackend() {
  const developmentPython = path.join(repositoryRoot, ".venv", "Scripts", "python.exe");
  const python = process.env.HEPHAESTUS_PYTHON || (isDevelopment && require("fs").existsSync(developmentPython) ? developmentPython : "python");
  const projectRoot = path.join(app.getPath("documents"), "HEPHAESTUS Projects");
  backend = spawn(python, ["-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"], {
    cwd: repositoryRoot,
    env: { ...process.env, HEPHAESTUS_PROJECT_ROOT: projectRoot },
    windowsHide: true,
    stdio: "pipe",
  });
  backend.stderr.on("data", (data) => console.error(`[HEPHAESTUS API] ${data}`));
}

async function createWindow() {
  startBackend();
  await waitForBackend();
  const window = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    backgroundColor: "#10141b",
    icon: path.join(repositoryRoot, "desktop", "src", "assets", "hephaestus-hammer-anvil.png"),
    webPreferences: { preload: path.join(__dirname, "preload.cjs"), contextIsolation: true, nodeIntegration: false },
  });
  if (isDevelopment) await window.loadURL("http://127.0.0.1:5173");
  else await window.loadFile(path.join(__dirname, "../dist/index.html"));
}

app.whenReady().then(createWindow).catch((error) => { console.error(error); app.quit(); });
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
app.on("before-quit", () => { if (backend && !backend.killed) backend.kill(); });
