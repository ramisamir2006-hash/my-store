'use strict';
// SQLite via Node's built-in module (no npm packages needed).
const { DatabaseSync } = require('node:sqlite');
const path = require('path');
const fs = require('fs');

const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
fs.mkdirSync(path.join(DATA_DIR, 'uploads'), { recursive: true });

const db = new DatabaseSync(path.join(DATA_DIR, 'karas.db'));
db.exec('PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;');

db.exec(`
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE COLLATE NOCASE,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('manager','staff')),
  pass TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE,
  email TEXT,
  pass TEXT,
  tier TEXT NOT NULL DEFAULT 'retail' CHECK (tier IN ('retail','semi','wholesale')),
  discount_pct REAL NOT NULL DEFAULT 0,
  address TEXT, city TEXT, notes TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  created_by TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  uid INTEGER NOT NULL,
  expires INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL UNIQUE COLLATE NOCASE,
  barcode TEXT UNIQUE,
  name TEXT NOT NULL,
  name_en TEXT,
  category TEXT NOT NULL,
  description TEXT, color TEXT, material TEXT,
  cost REAL NOT NULL DEFAULT 0,
  price_retail REAL NOT NULL DEFAULT 0,
  price_semi REAL NOT NULL DEFAULT 0,
  price_wholesale REAL NOT NULL DEFAULT 0,
  stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  min_stock INTEGER NOT NULL DEFAULT 5,
  images TEXT NOT NULL DEFAULT '[]',
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_cat ON products(category);
CREATE TABLE IF NOT EXISTS stock_moves (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  type TEXT NOT NULL,
  qty INTEGER NOT NULL,
  unit_cost REAL,
  note TEXT,
  ref_order INTEGER,
  user_name TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_moves_prod ON stock_moves(product_id);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER,
  customer_name TEXT, customer_phone TEXT,
  channel TEXT NOT NULL CHECK (channel IN ('shop','staff')),
  status TEXT NOT NULL CHECK (status IN ('pending','confirmed','shipped','delivered','cancelled')),
  paid INTEGER NOT NULL DEFAULT 0,
  tier TEXT NOT NULL DEFAULT 'retail',
  discount_pct REAL NOT NULL DEFAULT 0,
  subtotal REAL NOT NULL, discount_amount REAL NOT NULL DEFAULT 0,
  shipping REAL NOT NULL DEFAULT 0, total REAL NOT NULL,
  payment TEXT, note TEXT, address TEXT,
  payment_ref TEXT, payment_proof TEXT, card_txn TEXT, paid_at TEXT,
  created_by INTEGER, created_by_name TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE TABLE IF NOT EXISTS order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  code TEXT NOT NULL, name TEXT NOT NULL,
  qty INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  unit_cost REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS counters (key TEXT PRIMARY KEY, value INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, detail TEXT
);
`);

const stmtCache = new Map();
const prep = sql => { let s = stmtCache.get(sql); if (!s) { s = db.prepare(sql); stmtCache.set(sql, s); } return s; };
const get = (sql, ...p) => prep(sql).get(...p);
const all = (sql, ...p) => prep(sql).all(...p);
const run = (sql, ...p) => { const r = prep(sql).run(...p); return { changes: Number(r.changes), id: Number(r.lastInsertRowid) }; };

function tx(fn) {
  db.exec('BEGIN IMMEDIATE');
  try { const r = fn(); db.exec('COMMIT'); return r; }
  catch (e) { try { db.exec('ROLLBACK'); } catch (_) {} throw e; }
}

const DEFAULTS = {
  store_name: 'كاراس و أبو سيفين',
  store_phone: '01010055855 / 01070510005',
  store_address: '٤ عطفة العشماوي متفرع من حارة زويلة السيدة العذراء حالة الحديد',
  currency: 'ج.م',
  staff_max_discount: '100',
  default_min_stock: '5',
  shipping_fee: '0'
};
function getSettings() {
  const out = { ...DEFAULTS };
  for (const r of all('SELECT key, value FROM settings')) out[r.key] = r.value;
  return out;
}
function setSetting(key, value) {
  run('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', key, String(value));
}
function nextCounter(key) {
  const r = get('SELECT value FROM counters WHERE key=?', key);
  const v = (r ? r.value : 0) + 1;
  run('INSERT INTO counters(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', key, v);
  return v;
}
const nowIso = () => new Date().toISOString();
function audit(actor, action, detail) {
  run('INSERT INTO audit(ts,actor,action,detail) VALUES(?,?,?,?)', nowIso(), actor, action, detail ? String(detail).slice(0, 500) : null);
}

module.exports = { db, DATA_DIR, get, all, run, tx, getSettings, setSetting, nextCounter, nowIso, audit };
