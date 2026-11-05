'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const D = require('./db');
const { handle, HttpError } = require('./routes');

const PORT = Number(process.env.PORT) || 3000;
const PUBLIC = path.join(__dirname, '..', 'public');
const UPLOADS = path.join(D.DATA_DIR, 'uploads');
const TRUST_PROXY = process.env.TRUST_PROXY === '1';

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.webmanifest': 'application/manifest+json', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.ico': 'image/x-icon'
};

function secHeaders(res, https) {
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; manifest-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'same-origin');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Permissions-Policy', 'camera=(self), microphone=(), geolocation=()');
  if (https) res.setHeader('Strict-Transport-Security', 'max-age=31536000');
}

function parseCookies(h) {
  const out = {};
  for (const part of String(h || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0) { try { out[part.slice(0, i).trim()] = decodeURIComponent(part.slice(i + 1).trim()); } catch (_) {} }
  }
  return out;
}

function sendJson(res, status, obj, extraHeaders) {
  const body = JSON.stringify(obj);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'Content-Length': Buffer.byteLength(body), ...extraHeaders });
  res.end(body);
}

function serveFile(req, res, file, cache) {
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }); return res.end('Not found'); }
    const ext = path.extname(file).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream', 'Content-Length': st.size, 'Cache-Control': cache });
    if (req.method === 'HEAD') return res.end();
    fs.createReadStream(file).pipe(res);
  });
}

function serveStatic(req, res, pathname) {
  if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405); return res.end(); }
  let rel;
  try { rel = decodeURIComponent(pathname); } catch (_) { res.writeHead(400); return res.end(); }
  if (rel.includes('\0')) { res.writeHead(400); return res.end(); }

  if (rel.startsWith('/uploads/')) {
    const name = rel.slice(9);
    if (!/^[a-f0-9]{32}\.(jpg|png|webp)$/.test(name)) { res.writeHead(404); return res.end(); }
    return serveFile(req, res, path.join(UPLOADS, name), 'public, max-age=31536000, immutable');
  }
  if (['/shop', '/staff', '/manager'].includes(rel)) { res.writeHead(301, { Location: rel + '/' }); return res.end(); }
  if (rel.endsWith('/')) rel += 'index.html';
  const file = path.normalize(path.join(PUBLIC, rel));
  if (!file.startsWith(PUBLIC + path.sep)) { res.writeHead(403); return res.end(); }
  const ext = path.extname(file).toLowerCase();
  const cache = /\.(png|jpg|ico)$/.test(ext) ? 'public, max-age=86400' : 'no-cache';
  serveFile(req, res, file, cache);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  const https = req.socket.encrypted || (TRUST_PROXY && req.headers['x-forwarded-proto'] === 'https') || process.env.COOKIE_SECURE === '1';
  secHeaders(res, https);

  if (!url.pathname.startsWith('/api/')) return serveStatic(req, res, url.pathname);

  const setCookies = [];
  const ip = (TRUST_PROXY && String(req.headers['x-forwarded-for'] || '').split(',')[0].trim()) || req.socket.remoteAddress || '?';
  const c = {
    req, res, ip, pathname: url.pathname, q: Object.fromEntries(url.searchParams), body: {}, cookies: parseCookies(req.headers.cookie),
    setCookie(name, val, maxAge) {
      setCookies.push(`${name}=${val}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${Math.floor(maxAge)}${https ? '; Secure' : ''}`);
    },
    clearCookie(name) { setCookies.push(`${name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${https ? '; Secure' : ''}`); },
    readBody() {
      if (req.method === 'GET' || req.method === 'HEAD') return Promise.resolve();
      return new Promise((resolve, reject) => {
        const chunks = [];
        let size = 0;
        req.on('data', (d) => {
          size += d.length;
          if (size > c.bodyLimit) { reject(new HttpError(413, 'الطلب كبير جداً')); req.destroy(); return; }
          chunks.push(d);
        });
        req.on('end', () => {
          if (!size) return resolve();
          try {
            const j = JSON.parse(Buffer.concat(chunks).toString('utf8'));
            if (!j || typeof j !== 'object' || Array.isArray(j)) throw 0;
            c.body = j;
            resolve();
          } catch (_) { reject(new HttpError(400, 'بيانات غير صحيحة')); }
        });
        req.on('error', reject);
      });
    }
  };

  try {
    const out = await handle(c);
    const extra = setCookies.length ? { 'Set-Cookie': setCookies } : {};
    if (out && out.__raw) {
      res.writeHead(200, { 'Content-Type': out.type, 'Content-Length': out.__raw.length, 'Content-Disposition': `attachment; filename="${out.filename}"`, 'Cache-Control': 'no-store', ...extra });
      return res.end(out.__raw);
    }
    sendJson(res, 200, out === undefined ? { ok: true } : out, extra);
  } catch (e) {
    const extra = setCookies.length ? { 'Set-Cookie': setCookies } : {};
    if (e instanceof HttpError) return sendJson(res, e.status, { error: e.message }, extra);
    console.error(e);
    sendJson(res, 500, { error: 'خطأ في الخادم' }, extra);
  }
});

server.listen(PORT, () => console.log(`Karas system running on http://localhost:${PORT}  (data: ${D.DATA_DIR})`));

process.on('SIGTERM', () => { server.close(() => process.exit(0)); });
