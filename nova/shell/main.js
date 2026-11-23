// Nova's window: truly transparent (per-pixel), frameless, always on top, off the taskbar.
// Talks to Python over a local socket (127.0.0.1), one JSON message per line.
// (Not stdin/stdout: on Windows a GUI app's console pipes are unreliable.)
const { app, BrowserWindow, ipcMain, screen, protocol, net } = require('electron');
const path = require('path');
const readline = require('readline');
const sockets = require('net');
const { pathToFileURL } = require('url');

const BODY = path.join(__dirname, '..', 'body');
const opts = JSON.parse(process.env.NOVA_OPTS || '{}');
const link = sockets.connect(opts.port, '127.0.0.1');
link.setEncoding('utf8');
link.on('error', err => { console.error('link error', err); app.quit(); });
link.on('close', () => app.quit()); // Python stopped: close too
const send = msg => { if (!link.destroyed) link.write(JSON.stringify(msg) + '\n'); };

protocol.registerSchemesAsPrivileged([{ scheme: 'nova', privileges: { standard: true, secure: true, supportFetchAPI: true } }]);
app.commandLine.appendSwitch('disable-renderer-backgrounding');
app.commandLine.appendSwitch('ignore-gpu-blocklist');
// Nova's own profile folder (cache etc.), so nothing else can lock it
app.setPath('userData', path.join(__dirname, '..', '..', 'data', 'window-profile'));

let win = null;
let walkX = null;

// Nova's size: the window grows with him (it also needs room for the menu), and the 3D crew is scaled to fit.
// Same formula as body_electron.py.
let size = opts.size || 120;
const dims = s => {
  const W = Math.max(230, Math.round(s * 2.4)), H = Math.max(300, Math.round(s * 2.9));
  return { W, H, scale: (s / 120) * (300 / H) };
};
let { W: curW, H: curH } = dims(size);

// Always move with an explicit width and height. On Windows with display scaling (125%, 150%...)
// moving with setPosition makes the window creep a pixel bigger every call, so Nova grew while he crawled.
function place(x, y) {
  if (win) win.setBounds({ x: Math.round(x), y: Math.round(y), width: curW, height: curH });
}

function resizeTo(newSize) {
  if (!win) return;
  size = Math.max(40, Math.min(220, Math.round(newSize)));
  const b = win.getBounds(), d = dims(size);
  const cx = b.x + b.width / 2, bottom = b.y + b.height; // keep his feet where they are
  curW = d.W; curH = d.H;
  place(cx - curW / 2, bottom - curH);
  walkX = null;
  keepOnScreen();
  win.webContents.executeJavaScript(`window.nova && nova.setScale(${d.scale})`).catch(() => {});
  send({ event: 'resized', args: [size] });
}

function reportPosition() {
  if (!win) return;
  const b = win.getBounds();
  send({ event: 'moved', args: [b.x, b.y] });
}

function createWindow() {
  const { workArea } = screen.getPrimaryDisplay();
  const W = curW, H = curH;
  const right = (opts.corner || 'bottom-right').includes('right');
  const bottom = (opts.corner || 'bottom-right').includes('bottom');
  const saved = Number.isFinite(opts.x) && Number.isFinite(opts.y); // where you last put him
  win = new BrowserWindow({
    width: W, height: H,
    x: saved ? opts.x : right ? workArea.x + workArea.width - W - 8 : workArea.x + 8,
    y: saved ? opts.y : bottom ? workArea.y + workArea.height - H : workArea.y + 8,
    transparent: true, backgroundColor: '#00000000', frame: false, hasShadow: false, thickFrame: false,
    resizable: false, maximizable: false, fullscreenable: false, skipTaskbar: true, alwaysOnTop: true,
    show: false, title: 'Nova',
    webPreferences: { preload: path.join(__dirname, 'preload.js'), backgroundThrottling: false },
  });
  win.setAlwaysOnTop(true, 'screen-saver');
  win.setVisibleOnAllWorkspaces(true);
  win.setIgnoreMouseEvents(true, { forward: true }); // clicks pass through until the mouse is over Nova
  // report problems to Python's console instead of failing silently
  win.webContents.on('console-message', (e) => { if (e.level === 'error' || e.level === 'warning') send({ event: 'log', args: [`page: ${e.message}`] }); });
  win.webContents.on('did-fail-load', (_e, code, desc, url) => send({ event: 'log', args: [`load failed ${code} ${desc} ${url}`] }));
  win.webContents.on('render-process-gone', (_e, d) => send({ event: 'log', args: [`renderer gone: ${d.reason}`] }));
  win.loadURL('nova://app/index.html');
  win.once('ready-to-show', () => win.showInactive());
  setInterval(keepOnScreen, 1000);
  win.on('closed', () => { win = null; app.quit(); });

  // eyes follow the mouse anywhere on screen
  let last = '';
  setInterval(() => {
    if (!win || !win.isVisible()) return;
    const p = screen.getCursorScreenPoint(), b = win.getBounds();
    const nx = ((p.x - (b.x + b.width * 0.6)) / 500).toFixed(2), ny = ((p.y - (b.y + b.height * 0.45)) / 400).toFixed(2);
    if (nx + ny !== last) { last = nx + ny; win.webContents.executeJavaScript(`window.nova && nova.pointer(${nx}, ${ny})`).catch(() => {}); }
  }, 100);
}

app.whenReady().then(() => {
  protocol.handle('nova', req => {
    const file = path.normalize(path.join(BODY, decodeURIComponent(new URL(req.url).pathname)));
    if (!file.startsWith(BODY)) return new Response('no', { status: 403 });
    return net.fetch(pathToFileURL(file).toString());
  });
  createWindow();
});

ipcMain.on('api', (_e, name, args) => {
  if (!win) return;
  if (name === 'move_by') { const [x, y] = win.getPosition(); place(x + args[0], y + args[1]); walkX = null; return; }
  if (name === 'drag_end') { keepOnScreen(); reportPosition(); return; }
  if (name === 'resize_by') { resizeTo(size + Number(args[0] || 0)); return; }
  if (name === 'set_ignore') { win.setIgnoreMouseEvents(!!args[0], { forward: true }); return; }
  if (name === 'focus') { win.focus(); return; }
  if (name === 'set_shape') return; // not needed: this window is truly transparent
  send({ event: name, args });
});

// walking / crawling: slide the window along the screen, never past its edges
ipcMain.handle('nudge', (_e, dx) => {
  if (!win) return { hit_edge: false };
  const { workArea } = screen.getDisplayMatching(win.getBounds());
  const [x, y] = win.getPosition(), w = win.getBounds().width;
  const lo = workArea.x, hi = workArea.x + workArea.width - w;
  walkX = Math.max(lo, Math.min(hi, walkX ?? x)) + dx;
  const hit = walkX <= lo || walkX >= hi;
  walkX = Math.max(lo, Math.min(hi, walkX));
  if (Math.round(walkX) !== x) place(walkX, y);
  return { hit_edge: hit, x: walkX, lo, hi };
});

function cornerPosition() {
  const { workArea } = screen.getPrimaryDisplay();
  const W = curW, H = curH;
  const corner = opts.corner || 'bottom-right';
  return [corner.includes('right') ? workArea.x + workArea.width - W - 8 : workArea.x + 8,
          corner.includes('bottom') ? workArea.y + workArea.height - H : workArea.y + 8];
}

// safety net: if Nova ever ends up partly off-screen (or the window size drifted), put him back
function keepOnScreen() {
  if (!win || !win.isVisible()) return;
  const b = win.getBounds();
  const { workArea: a } = screen.getDisplayMatching(b);
  const x = Math.max(a.x, Math.min(a.x + a.width - b.width, b.x));
  const y = Math.max(a.y, Math.min(a.y + a.height - b.height, b.y));
  if (x !== b.x || y !== b.y || b.width !== curW || b.height !== curH) { place(x, y); walkX = null; }
}

readline.createInterface({ input: link }).on('line', line => {
  let msg;
  try { msg = JSON.parse(line); } catch { return; }
  if (!win) return;
  if (msg.js) win.webContents.executeJavaScript(msg.js).catch(err => send({ event: 'log', args: [String(err)] }));
  else if (msg.cmd === 'show') win.showInactive();
  else if (msg.cmd === 'hide') win.hide();
  else if (msg.cmd === 'quit') app.quit();
  else if (msg.cmd === 'home') { place(...cornerPosition()); walkX = null; win.showInactive(); reportPosition(); }
  else if (msg.cmd === 'resize_by') resizeTo(size + Number(msg.delta || 0));
  else if (msg.cmd === 'resize_to') resizeTo(Number(msg.size) || size);
});
app.on('window-all-closed', () => app.quit());
