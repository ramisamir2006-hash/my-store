'use strict';
// Consistent daily backup of the database (+ prune old ones). Run: docker compose exec -T app node server/backup.js
const { DatabaseSync } = require('node:sqlite');
const fs = require('fs');
const path = require('path');
const DATA = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
const dir = path.join(DATA, 'backups');
fs.mkdirSync(dir, { recursive: true });
const day = new Date().toISOString().slice(0, 10);
const file = path.join(dir, `karas-${day}.db`);
if (fs.existsSync(file)) fs.unlinkSync(file);
const db = new DatabaseSync(path.join(DATA, 'karas.db'));
db.exec(`VACUUM INTO '${file.replace(/'/g, "''")}'`);
db.close();
const keep = Number(process.env.BACKUP_KEEP_DAYS) || 14;
for (const f of fs.readdirSync(dir)) {
  const p = path.join(dir, f);
  if (/^karas-.*\.db$/.test(f) && Date.now() - fs.statSync(p).mtimeMs > keep * 864e5) fs.unlinkSync(p);
}
console.log('backup ok:', file);
