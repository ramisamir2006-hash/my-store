'use strict';
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const D = require('./db');
const { get, all, run, tx, nowIso, audit } = D;

/* ---------- helpers ---------- */
class HttpError extends Error { constructor(status, msg) { super(msg); this.status = status; } }
const bad = (m) => new HttpError(400, m);
const forbidden = (m) => new HttpError(403, m || 'غير مسموح لك بهذا الإجراء');
const notFound = (m) => new HttpError(404, m || 'غير موجود');
const round2 = (n) => Math.round((Number(n) + Number.EPSILON) * 100) / 100;

function num(v, name, { min = 0, max = 1e9, int = false, def } = {}) {
  if (v === undefined || v === null || v === '') { if (def !== undefined) return def; throw bad(`${name} مطلوب`); }
  const n = Number(v);
  if (!Number.isFinite(n)) throw bad(`${name} غير صحيح`);
  if (int && !Number.isInteger(n)) throw bad(`${name} يجب أن يكون رقماً صحيحاً`);
  if (n < min || n > max) throw bad(`${name} يجب أن يكون بين ${min} و ${max}`);
  return n;
}
function str(v, name, { max = 200, required = false } = {}) {
  if (v === undefined || v === null) v = '';
  if (typeof v !== 'string') throw bad(`${name} غير صحيح`);
  v = v.trim();
  if (required && !v) throw bad(`${name} مطلوب`);
  if (v.length > max) throw bad(`${name} طويل جداً`);
  return v;
}
const normPhone = (v) => {
  let s = str(v, 'رقم الموبايل', { required: true, max: 30 });
  s = s.replace(/[٠-٩]/g, (d) => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[^\d+]/g, '');
  if (s.replace(/\D/g, '').length < 8) throw bad('رقم الموبايل غير صحيح');
  return s;
};
const likeEsc = (s) => '%' + s.replace(/[\\%_]/g, (m) => '\\' + m) + '%';

/* ---------- passwords & sessions ---------- */
function hashPw(pw) {
  const salt = crypto.randomBytes(16);
  return salt.toString('hex') + ':' + crypto.scryptSync(pw, salt, 64).toString('hex');
}
const DUMMY = hashPw('dummy-password');
function checkPw(pw, stored) {
  const [s, h] = String(stored || DUMMY).split(':');
  const hh = crypto.scryptSync(String(pw), Buffer.from(s, 'hex'), 64);
  const hb = Buffer.from(h, 'hex');
  return !!stored && hb.length === hh.length && crypto.timingSafeEqual(hb, hh);
}
function checkNewPw(pw) {
  if (typeof pw !== 'string' || pw.length < 6) throw bad('كلمة السر يجب ألا تقل عن ٦ أحرف');
  if (pw.length > 100) throw bad('كلمة السر طويلة جداً');
  return pw;
}
const sha = (t) => crypto.createHash('sha256').update(t).digest('hex');
const COOKIE = { customer: 'ks_c', staff: 'ks_s' };
const TTL = { customer: 30 * 864e5, staff: 7 * 864e5 };

function newSession(c, kind, uid) {
  const token = crypto.randomBytes(32).toString('hex');
  run('DELETE FROM sessions WHERE expires < ?', Date.now());
  run('INSERT INTO sessions(token,kind,uid,expires) VALUES(?,?,?,?)', sha(token), kind, uid, Date.now() + TTL[kind]);
  c.setCookie(COOKIE[kind], token, TTL[kind] / 1000);
}
function sessionUser(c, kind) {
  const token = c.cookies[COOKIE[kind]];
  if (!token) return null;
  const s = get('SELECT * FROM sessions WHERE token=? AND kind=? AND expires>?', sha(token), kind, Date.now());
  if (!s) return null;
  const u = kind === 'staff'
    ? get('SELECT id,username,name,role FROM users WHERE id=? AND active=1', s.uid)
    : get('SELECT * FROM customers WHERE id=? AND active=1 AND pass IS NOT NULL', s.uid);
  return u || null;
}

/* ---------- login throttling ---------- */
const fails = new Map();
function throttle(key) {
  const f = fails.get(key);
  if (f && f.n >= 8 && Date.now() - f.t < 15 * 60e3) throw new HttpError(429, 'محاولات كثيرة. حاول بعد ١٥ دقيقة');
}
function failed(key) {
  const f = fails.get(key);
  if (!f || Date.now() - f.t > 15 * 60e3) fails.set(key, { n: 1, t: Date.now() });
  else { f.n++; f.t = Date.now(); }
}

/* ---------- Cairo time ---------- */
const cairoFmt = new Intl.DateTimeFormat('en-CA', { timeZone: 'Africa/Cairo', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' });
function cairoParts(d) { const o = {}; for (const p of cairoFmt.formatToParts(d)) o[p.type] = Number(p.value); return o; }
const cairoDay = (iso) => { const p = cairoParts(new Date(iso)); return `${p.year}-${String(p.month).padStart(2, '0')}-${String(p.day).padStart(2, '0')}`; };
function cairoStartUtc(day) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(day || '');
  if (!m) throw bad('تاريخ غير صحيح');
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const mid = Date.UTC(y, mo - 1, d);
  let g = mid;
  for (let i = 0; i < 3; i++) {
    const p = cairoParts(new Date(g));
    g = mid - (Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second) - g);
  }
  return new Date(g);
}
const addDay = (day, n) => new Date(Date.UTC(...day.split('-').map((x, i) => (i === 1 ? Number(x) - 1 : Number(x))).map((x, i) => (i === 2 ? x + n : x))))
  .toISOString().slice(0, 10);
function rangeFromQuery(q, defDays) {
  const today = cairoDay(nowIso());
  const to = q.to || today;
  const from = q.from || addDay(to, -(defDays - 1));
  return { from, to, fromIso: cairoStartUtc(from).toISOString(), toIso: cairoStartUtc(addDay(to, 1)).toISOString() };
}

/* ---------- settings & categories ---------- */
const DEFAULT_CATS = [
  { name: 'خواتم', prefix: 'RG' }, { name: 'أساور', prefix: 'BR' }, { name: 'سلاسل وقلادات', prefix: 'NK' },
  { name: 'أقراط', prefix: 'ER' }, { name: 'خلاخيل', prefix: 'AN' }, { name: 'أطقم', prefix: 'ST' },
  { name: 'دبابيس وإكسسوارات شعر', prefix: 'HA' }, { name: 'أخرى', prefix: 'OT' }
];
function categories() {
  const r = get("SELECT value FROM settings WHERE key='categories'");
  try { const a = JSON.parse(r.value); if (Array.isArray(a) && a.length) return a; } catch (_) {}
  return DEFAULT_CATS;
}
function publicSettings() {
  const s = D.getSettings();
  return {
    store_name: s.store_name, store_phone: s.store_phone, store_address: s.store_address, currency: s.currency, shipping_fee: Number(s.shipping_fee) || 0, categories: categories().map((c) => c.name),
    payment: {
      cash: true, card: !!paymobCfg(),
      transfer: !!(s.bank_account_number || s.bank_iban || s.wallet_number || s.instapay_handle),
      bank_name: s.bank_name || '', bank_account_name: s.bank_account_name || '', bank_account_number: s.bank_account_number || '',
      bank_iban: s.bank_iban || '', wallet_number: s.wallet_number || '', instapay_handle: s.instapay_handle || '', payment_note: s.payment_note || ''
    }
  };
}

/* ---------- products & pricing ---------- */
function tierPrice(p, tier) {
  let v = tier === 'wholesale' ? p.price_wholesale : tier === 'semi' ? p.price_semi : p.price_retail;
  if (!(v > 0)) v = tier === 'wholesale' ? (p.price_semi > 0 ? p.price_semi : p.price_retail) : p.price_retail;
  return round2(v);
}
function productOut(p, mode, cust) {
  const o = {
    id: p.id, code: p.code, name: p.name, name_en: p.name_en, category: p.category, description: p.description,
    color: p.color, material: p.material, images: JSON.parse(p.images || '[]'), active: !!p.active
  };
  if (mode === 'customer') {
    const tier = cust ? cust.tier : 'retail', d = cust ? cust.discount_pct : 0;
    o.price = tierPrice(p, tier);
    o.final_price = round2(o.price * (1 - d / 100));
    o.available = p.stock;
    return o;
  }
  Object.assign(o, { barcode: p.barcode, stock: p.stock, min_stock: p.min_stock, price_retail: p.price_retail, price_semi: p.price_semi, price_wholesale: p.price_wholesale, updated_at: p.updated_at });
  if (mode === 'manager') o.cost = p.cost;
  return o;
}
function productFilters(q, params, { onlyActive }) {
  let where = '1=1';
  if (onlyActive) where += ' AND active=1';
  else if (q.active === '1' || q.active === '0') { where += ' AND active=?'; params.push(Number(q.active)); }
  if (q.cat) { where += ' AND category=?'; params.push(String(q.cat)); }
  if (q.ids) { const ids = String(q.ids).split(',').map(Number).filter((n) => Number.isInteger(n) && n > 0).slice(0, 100); where += ` AND id IN (${ids.length ? ids.join(',') : '0'})`; }
  if (q.q) {
    const l = likeEsc(String(q.q).trim().slice(0, 60));
    where += " AND (name LIKE ? ESCAPE '\\' OR name_en LIKE ? ESCAPE '\\' OR code LIKE ? ESCAPE '\\' OR barcode LIKE ? ESCAPE '\\')";
    params.push(l, l, l, l);
  }
  if (q.low === '1') where += ' AND active=1 AND stock <= min_stock';
  return where;
}
function paging(q) {
  const limit = Math.min(Math.max(parseInt(q.limit) || 100, 1), 500);
  const offset = Math.max(parseInt(q.offset) || 0, 0);
  return { limit, offset };
}
function uniqueErr(e, map) {
  if (/UNIQUE/i.test(String(e.message))) {
    for (const k of Object.keys(map)) if (String(e.message).includes(k)) return new HttpError(409, map[k]);
    return new HttpError(409, 'قيمة مكررة');
  }
  return e;
}
function nextCode(categoryName) {
  const cat = categories().find((c) => c.name === categoryName);
  const prefix = (cat ? cat.prefix : 'OT').toUpperCase();
  for (let i = 0; i < 1000; i++) {
    const code = `KS-${prefix}-${String(D.nextCounter('code_' + prefix)).padStart(4, '0')}`;
    if (!get('SELECT 1 FROM products WHERE code=?', code)) return code;
  }
  throw new Error('code generation failed');
}
function readProductBody(b, existing) {
  const e = existing || {};
  const has = (k) => b[k] !== undefined;
  const cats = categories().map((c) => c.name);
  const category = has('category') ? str(b.category, 'القسم', { required: true, max: 60 }) : e.category;
  if (!existing && !cats.includes(category)) throw bad('القسم غير موجود');
  const barcode = has('barcode') ? (str(b.barcode, 'الباركود', { max: 40 }) || null) : (e.barcode ?? null);
  if (barcode && !/^[A-Za-z0-9\-_.]{4,40}$/.test(barcode)) throw bad('الباركود غير صحيح (حروف وأرقام فقط)');
  let images = e.images ? JSON.parse(e.images) : [];
  if (has('images')) {
    if (!Array.isArray(b.images) || b.images.length > 6) throw bad('الصور: حد أقصى ٦');
    images = b.images.map((u) => { if (!/^\/uploads\/[a-f0-9]{32}\.(jpg|png|webp)$/.test(u)) throw bad('رابط صورة غير صحيح'); return u; });
  }
  const price = (k, nm) => (has(k) ? num(b[k], nm, { max: 1e7 }) : e[k] || 0);
  return {
    name: has('name') ? str(b.name, 'اسم المنتج', { required: true, max: 120 }) : e.name,
    name_en: has('name_en') ? str(b.name_en, 'الاسم بالإنجليزي', { max: 120 }) : e.name_en || '',
    category, barcode,
    description: has('description') ? str(b.description, 'الوصف', { max: 1000 }) : e.description || '',
    color: has('color') ? str(b.color, 'اللون', { max: 40 }) : e.color || '',
    material: has('material') ? str(b.material, 'الخامة', { max: 60 }) : e.material || '',
    cost: price('cost', 'سعر الشراء'), price_retail: price('price_retail', 'سعر القطاعي'),
    price_semi: price('price_semi', 'سعر نص الجملة'), price_wholesale: price('price_wholesale', 'سعر الجملة'),
    min_stock: has('min_stock') ? num(b.min_stock, 'حد التنبيه', { int: true, max: 1e6 }) : (e.min_stock ?? Number(D.getSettings().default_min_stock)),
    images: JSON.stringify(images)
  };
}

function addMove(productId, type, qty, unitCost, note, ref, user) {
  run('INSERT INTO stock_moves(product_id,type,qty,unit_cost,note,ref_order,user_name,created_at) VALUES(?,?,?,?,?,?,?,?)',
    productId, type, qty, unitCost ?? null, note || null, ref || null, user || null, nowIso());
}

/* ---------- orders ---------- */
const SALE_STATUSES = "('confirmed','shipped','delivered')";
const TRANSITIONS = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['shipped', 'delivered', 'cancelled'],
  shipped: ['delivered', 'cancelled'],
  delivered: ['cancelled'],
  cancelled: []
};
function orderItems(id) { return all('SELECT product_id,code,name,qty,unit_price,unit_cost FROM order_items WHERE order_id=? ORDER BY id', id); }
function orderOut(o, mode, withItems) {
  const out = { ...o, paid: !!o.paid };
  if (withItems) {
    out.items = orderItems(o.id).map((i) => {
      const r = { ...i, line_total: round2(i.qty * i.unit_price) };
      if (mode !== 'manager') delete r.unit_cost;
      return r;
    });
  }
  if (mode === 'manager') {
    const cost = get('SELECT COALESCE(SUM(qty*unit_cost),0) c FROM order_items WHERE order_id=?', o.id).c;
    out.cost_total = round2(cost);
    out.profit = round2(o.subtotal - o.discount_amount - cost);
  }
  return out;
}
function createOrder(a) {
  const settings = D.getSettings();
  if (!Array.isArray(a.items) || !a.items.length) throw bad('الطلب فارغ');
  if (a.items.length > 200) throw bad('عدد البنود كبير');
  const merged = new Map();
  for (const it of a.items) {
    const qty = num(it.qty, 'الكمية', { min: 1, max: 100000, int: true });
    let p = null;
    if (it.product_id) p = get('SELECT * FROM products WHERE id=?', Number(it.product_id));
    else if (it.code) p = get('SELECT * FROM products WHERE code=? OR barcode=?', String(it.code), String(it.code));
    if (!p || !p.active) throw bad('منتج غير موجود أو غير متاح');
    merged.set(p.id, (merged.get(p.id) || 0) + qty);
  }
  const channel = a.channel;
  const status = channel === 'staff' ? 'confirmed' : 'pending';
  const now = nowIso();
  return tx(() => {
    let subtotal = 0;
    const lines = [];
    for (const [pid, qty] of merged) {
      const p = get('SELECT * FROM products WHERE id=?', pid);
      if (p.stock < qty) throw bad(`الكمية غير كافية: ${p.name} (المتاح ${p.stock})`);
      const unit = tierPrice(p, a.tier);
      subtotal += unit * qty;
      lines.push({ p, qty, unit });
    }
    subtotal = round2(subtotal);
    const discAmt = round2(subtotal * a.discountPct / 100);
    const total = round2(subtotal - discAmt + a.shipping);
    const r = run(`INSERT INTO orders(customer_id,customer_name,customer_phone,channel,status,paid,tier,discount_pct,subtotal,discount_amount,shipping,total,payment,note,address,created_by,created_by_name,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      a.customer ? a.customer.id : null, a.customerName || (a.customer && a.customer.name) || null, a.customerPhone || (a.customer && a.customer.phone) || null,
      channel, status, a.paid ? 1 : 0, a.tier, a.discountPct, subtotal, discAmt, a.shipping, total, a.payment || null, a.note || null, a.address || null,
      a.actor ? a.actor.id : null, a.actor ? a.actor.name : null, now, now);
    for (const l of lines) {
      run('INSERT INTO order_items(order_id,product_id,code,name,qty,unit_price,unit_cost) VALUES(?,?,?,?,?,?,?)', r.id, l.p.id, l.p.code, l.p.name, l.qty, l.unit, l.p.cost);
      if (status === 'confirmed') {
        run('UPDATE products SET stock=stock-?, updated_at=? WHERE id=?', l.qty, now, l.p.id);
        addMove(l.p.id, 'sale', -l.qty, l.p.cost, null, r.id, a.actor && a.actor.name);
      }
    }
    return r.id;
  });
}
function changeStatus(id, to, actor) {
  return tx(() => {
    const o = get('SELECT * FROM orders WHERE id=?', id);
    if (!o) throw notFound('الطلب غير موجود');
    if (!TRANSITIONS[o.status].includes(to)) throw bad('لا يمكن تغيير الحالة بهذا الشكل');
    if (to === 'cancelled' && (o.status === 'shipped' || o.status === 'delivered') && actor.role !== 'manager') throw forbidden('إلغاء طلب تم شحنه أو تسليمه للمدير فقط');
    const now = nowIso();
    const items = orderItems(id);
    if (o.status === 'pending' && to === 'confirmed') {
      for (const i of items) {
        const p = get('SELECT stock,name FROM products WHERE id=?', i.product_id);
        if (p.stock < i.qty) throw bad(`الكمية غير كافية: ${p.name} (المتاح ${p.stock})`);
      }
      for (const i of items) {
        run('UPDATE products SET stock=stock-?, updated_at=? WHERE id=?', i.qty, now, i.product_id);
        addMove(i.product_id, 'sale', -i.qty, i.unit_cost, null, id, actor.name);
      }
    } else if (to === 'cancelled' && o.status !== 'pending') {
      for (const i of items) {
        run('UPDATE products SET stock=stock+?, updated_at=? WHERE id=?', i.qty, now, i.product_id);
        addMove(i.product_id, 'cancel', i.qty, i.unit_cost, `إلغاء طلب #${id}`, id, actor.name);
      }
    }
    run('UPDATE orders SET status=?, updated_at=? WHERE id=?', to, now, id);
    audit(actor.name, 'order.status', `#${id} ${o.status}→${to}`);
    return get('SELECT * FROM orders WHERE id=?', id);
  });
}
function staffCanSee(o, user) { return user.role === 'manager' || o.channel === 'shop' || o.created_by === user.id; }

function customerOut(c) {
  const { pass, ...rest } = c;
  return { ...rest, active: !!c.active, has_login: !!pass };
}
function customerStats(id) {
  return get(`SELECT COUNT(*) orders, COALESCE(SUM(total),0) spent,
    COALESCE(SUM(CASE WHEN paid=0 THEN total ELSE 0 END),0) unpaid FROM orders WHERE customer_id=? AND status IN ${SALE_STATUSES}`, id);
}

/* ---------- reports ---------- */
function report(fromIso, toIso, includeProfit) {
  const orders = all(`SELECT * FROM orders WHERE status IN ${SALE_STATUSES} AND created_at>=? AND created_at<? ORDER BY created_at`, fromIso, toIso);
  const itemRows = all(`SELECT oi.* , o.created_at FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE o.status IN ${SALE_STATUSES} AND o.created_at>=? AND o.created_at<?`, fromIso, toIso);
  const costByOrder = new Map(), prod = new Map();
  for (const i of itemRows) {
    costByOrder.set(i.order_id, (costByOrder.get(i.order_id) || 0) + i.qty * i.unit_cost);
    const e = prod.get(i.product_id) || { code: i.code, name: i.name, qty: 0, revenue: 0, profit: 0 };
    e.qty += i.qty; e.revenue += i.qty * i.unit_price; e.profit += i.qty * (i.unit_price - i.unit_cost);
    prod.set(i.product_id, e);
  }
  const days = new Map(), staff = new Map(), channel = {}, tier = {};
  let sales = 0, profit = 0, discounts = 0, unpaid = 0;
  for (const o of orders) {
    const pr = o.subtotal - o.discount_amount - (costByOrder.get(o.id) || 0);
    sales += o.total; profit += pr; discounts += o.discount_amount;
    if (!o.paid) unpaid += o.total;
    const d = cairoDay(o.created_at);
    const de = days.get(d) || { day: d, orders: 0, sales: 0, profit: 0 }; de.orders++; de.sales += o.total; de.profit += pr; days.set(d, de);
    const sn = o.created_by_name || 'المتجر الإلكتروني';
    const se = staff.get(sn) || { name: sn, orders: 0, sales: 0, discounts: 0 }; se.orders++; se.sales += o.total; se.discounts += o.discount_amount; staff.set(sn, se);
    channel[o.channel] = (channel[o.channel] || 0) + o.total;
    tier[o.tier] = (tier[o.tier] || 0) + o.total;
  }
  const top = [...prod.values()].sort((a, b) => b.revenue - a.revenue).slice(0, 10)
    .map((e) => ({ code: e.code, name: e.name, qty: e.qty, revenue: round2(e.revenue), ...(includeProfit ? { profit: round2(e.profit) } : {}) }));
  const out = {
    orders: orders.length, sales: round2(sales), discounts: round2(discounts), unpaid: round2(unpaid),
    by_day: [...days.values()].map((d) => ({ ...d, sales: round2(d.sales), profit: includeProfit ? round2(d.profit) : undefined })),
    by_staff: [...staff.values()].map((s) => ({ ...s, sales: round2(s.sales), discounts: round2(s.discounts) })),
    by_channel: channel, by_tier: tier, top_products: top
  };
  if (includeProfit) out.profit = round2(profit);
  return out;
}

/* ---------- Paymob (card payments, hosted page: card data never touches this server) ---------- */
function paymobCfg() {
  const e = process.env;
  if (!(e.PAYMOB_API_KEY && e.PAYMOB_INTEGRATION_ID && e.PAYMOB_IFRAME_ID && e.PAYMOB_HMAC)) return null;
  return { key: e.PAYMOB_API_KEY, integration: e.PAYMOB_INTEGRATION_ID, iframe: e.PAYMOB_IFRAME_ID, hmac: e.PAYMOB_HMAC, base: (e.PAYMOB_BASE || 'https://accept.paymob.com').replace(/\/$/, '') };
}
async function pmPost(url, body) {
  let r;
  try {
    r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(20000) });
  } catch (_) { throw new HttpError(502, 'تعذّر الاتصال ببوابة الدفع، حاول لاحقاً'); }
  let j = null; try { j = await r.json(); } catch (_) {}
  if (!r.ok || !j) { console.error('paymob error', r.status, JSON.stringify(j).slice(0, 300)); throw new HttpError(502, 'بوابة الدفع رفضت العملية، حاول لاحقاً أو اختر طريقة دفع أخرى'); }
  return j;
}
const HMAC_FIELDS = ['amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction', 'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded', 'is_standalone_payment', 'is_voided', 'order.id', 'owner', 'pending', 'source_data.pan', 'source_data.sub_type', 'source_data.type', 'success'];
function paymobHmacOk(obj, given, secret) {
  const pick = (o, path) => path.split('.').reduce((a, k) => (a == null ? a : a[k]), o);
  const str = HMAC_FIELDS.map((f) => { const v = pick(obj, f); return v === undefined || v === null ? '' : String(v); }).join('');
  const calc = crypto.createHmac('sha512', secret).update(str).digest('hex');
  const a = Buffer.from(calc), b = Buffer.from(String(given || ''));
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
const truthy = (v) => v === true || v === 'true';

/* ---------- uploads ---------- */
function saveImage(dataUrl) {
  const m = /^data:image\/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)$/.exec(String(dataUrl || ''));
  if (!m) throw bad('صورة غير صحيحة');
  const buf = Buffer.from(m[2], 'base64');
  if (buf.length > 3 * 1024 * 1024) throw bad('الصورة كبيرة (الحد ٣ ميجا)');
  const ok = (m[1] === 'jpeg' && buf[0] === 0xff && buf[1] === 0xd8) ||
    (m[1] === 'png' && buf.slice(0, 4).toString('hex') === '89504e47') ||
    (m[1] === 'webp' && buf.slice(0, 4).toString() === 'RIFF' && buf.slice(8, 12).toString() === 'WEBP');
  if (!ok) throw bad('ملف الصورة تالف');
  const ext = m[1] === 'jpeg' ? 'jpg' : m[1];
  const name = crypto.randomBytes(16).toString('hex') + '.' + ext;
  fs.writeFileSync(path.join(D.DATA_DIR, 'uploads', name), buf);
  return '/uploads/' + name;
}

/* ---------- route table ---------- */
const routes = [];
function R(method, pattern, auth, handler, opts = {}) {
  const keys = [];
  const re = new RegExp('^' + pattern.replace(/:(\w+)/g, (_, k) => { keys.push(k); return '([^/]+)'; }) + '$');
  routes.push({ method, re, keys, auth, handler, big: !!opts.big, noCsrf: !!opts.noCsrf });
}
const idOf = (c) => { const n = parseInt(c.p.id, 10); if (!(n > 0)) throw notFound(); return n; };

// --- setup & public
R('GET', '/api/health', 'public', () => ({ ok: true }));
R('GET', '/api/setup/status', 'public', () => ({ needed: get('SELECT COUNT(*) n FROM users').n === 0 }));
R('POST', '/api/setup', 'public', (c) => {
  const b = c.body;
  const r = tx(() => {
    if (get('SELECT COUNT(*) n FROM users').n > 0) throw forbidden('تم الإعداد من قبل');
    const name = str(b.name, 'الاسم', { required: true, max: 80 });
    const username = str(b.username, 'اسم المستخدم', { required: true, max: 40 });
    if (!/^[A-Za-z0-9_.\-]{3,40}$/.test(username)) throw bad('اسم المستخدم: حروف إنجليزية وأرقام فقط (٣ أحرف على الأقل)');
    const id = run('INSERT INTO users(username,name,role,pass,active,created_at) VALUES(?,?,?,?,1,?)', username, name, 'manager', hashPw(checkNewPw(b.password)), nowIso()).id;
    if (b.store_name) D.setSetting('store_name', str(b.store_name, 'اسم المتجر', { max: 80 }));
    audit(name, 'setup', 'manager created');
    return id;
  });
  newSession(c, 'staff', r);
  return { ok: true };
});
R('GET', '/api/settings/public', 'public', () => publicSettings());

R('GET', '/api/catalog', 'public', (c) => {
  const params = [];
  const where = productFilters(c.q, params, { onlyActive: true });
  const { limit, offset } = paging(c.q);
  const rows = all(`SELECT * FROM products WHERE ${where} ORDER BY id DESC LIMIT ? OFFSET ?`, ...params, limit, offset);
  const total = get(`SELECT COUNT(*) n FROM products WHERE ${where}`, ...params).n;
  return { total, items: rows.map((p) => productOut(p, 'customer', c.cust)) };
}, {});

// --- auth
R('POST', '/api/auth/staff/login', 'public', (c) => {
  const username = str(c.body.username, 'اسم المستخدم', { required: true, max: 40 });
  const key = 's:' + c.ip + ':' + username.toLowerCase();
  throttle(key);
  const u = get('SELECT * FROM users WHERE username=?', username);
  if (!checkPw(c.body.password, u && u.pass) || !u.active) { failed(key); throw new HttpError(401, 'اسم المستخدم أو كلمة السر غير صحيحة'); }
  fails.delete(key);
  newSession(c, 'staff', u.id);
  return { user: { id: u.id, username: u.username, name: u.name, role: u.role } };
});
R('POST', '/api/auth/customer/login', 'public', (c) => {
  const phone = normPhone(c.body.phone);
  const key = 'c:' + c.ip + ':' + phone;
  throttle(key);
  const u = get('SELECT * FROM customers WHERE phone=?', phone);
  if (!checkPw(c.body.password, u && u.pass) || !u.active) { failed(key); throw new HttpError(401, 'رقم الموبايل أو كلمة السر غير صحيحة'); }
  fails.delete(key);
  newSession(c, 'customer', u.id);
  return { customer: customerOut(u) };
});
R('POST', '/api/auth/customer/register', 'public', (c) => {
  const key = 'r:' + c.ip;
  throttle(key);
  const b = c.body;
  const name = str(b.name, 'الاسم', { required: true, max: 80 });
  const phone = normPhone(b.phone);
  const pass = checkNewPw(b.password);
  const ex = get('SELECT id,pass FROM customers WHERE phone=?', phone);
  if (ex) {
    failed(key);
    throw new HttpError(409, ex.pass ? 'هذا الرقم مسجل بالفعل. سجّل الدخول' : 'هذا الرقم مسجل لدينا. تواصل مع المتجر لتفعيل حسابك');
  }
  const id = run('INSERT INTO customers(name,phone,email,pass,tier,discount_pct,address,city,created_at,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)',
    name, phone, str(b.email, 'البريد', { max: 100 }) || null, hashPw(pass), 'retail', 0, str(b.address, 'العنوان', { max: 300 }), str(b.city, 'المدينة', { max: 60 }), nowIso(), 'self').id;
  newSession(c, 'customer', id);
  return { customer: customerOut(get('SELECT * FROM customers WHERE id=?', id)) };
});
R('POST', '/api/auth/logout', 'public', (c) => {
  for (const k of ['customer', 'staff']) {
    const t = c.cookies[COOKIE[k]];
    if (t) run('DELETE FROM sessions WHERE token=?', sha(t));
    c.clearCookie(COOKIE[k]);
  }
  return { ok: true };
});

// --- customer area
R('GET', '/api/my/me', 'customer', (c) => ({ customer: customerOut(c.cust), settings: publicSettings() }));
R('PATCH', '/api/my/me', 'customer', (c) => {
  const b = c.body, cu = c.cust;
  if (b.new_password !== undefined) {
    if (!checkPw(b.current_password, cu.pass)) throw bad('كلمة السر الحالية غير صحيحة');
    run('UPDATE customers SET pass=? WHERE id=?', hashPw(checkNewPw(b.new_password)), cu.id);
  }
  run('UPDATE customers SET name=?, email=?, address=?, city=? WHERE id=?',
    b.name !== undefined ? str(b.name, 'الاسم', { required: true, max: 80 }) : cu.name,
    b.email !== undefined ? str(b.email, 'البريد', { max: 100 }) || null : cu.email,
    b.address !== undefined ? str(b.address, 'العنوان', { max: 300 }) : cu.address,
    b.city !== undefined ? str(b.city, 'المدينة', { max: 60 }) : cu.city, cu.id);
  return { customer: customerOut(get('SELECT * FROM customers WHERE id=?', cu.id)) };
});
R('GET', '/api/my/orders', 'customer', (c) => ({
  items: all('SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 200', c.cust.id).map((o) => orderOut(o, 'customer', true))
}));
R('POST', '/api/my/orders', 'customer', (c) => {
  const cu = c.cust, b = c.body;
  const address = str(b.address ?? cu.address, 'العنوان', { required: true, max: 300 });
  const id = createOrder({
    items: b.items, customer: cu, channel: 'shop', tier: cu.tier, discountPct: cu.discount_pct,
    shipping: Number(D.getSettings().shipping_fee) || 0, payment: ['cash', 'transfer', 'card'].includes(b.payment) ? b.payment : 'cash',
    note: str(b.note, 'ملاحظات', { max: 500 }), address
  });
  audit('customer:' + cu.phone, 'order.create', '#' + id);
  return { order: orderOut(get('SELECT * FROM orders WHERE id=?', id), 'customer', true) };
});
R('POST', '/api/my/orders/:id/cancel', 'customer', (c) => {
  const id = idOf(c);
  tx(() => {
    const o = get('SELECT * FROM orders WHERE id=? AND customer_id=?', id, c.cust.id);
    if (!o) throw notFound();
    if (o.status !== 'pending') throw bad('يمكن إلغاء الطلب قبل تأكيده فقط. تواصل مع المتجر');
    run("UPDATE orders SET status='cancelled', updated_at=? WHERE id=?", nowIso(), id);
  });
  return { ok: true };
});

// --- customer payments
const uploadsToday = new Map();
R('POST', '/api/my/uploads', 'customer', (c) => {
  const k = c.cust.id + ':' + cairoDay(nowIso());
  const n = (uploadsToday.get(k) || 0) + 1;
  if (n > 10) throw new HttpError(429, 'تجاوزت الحد اليومي لرفع الصور');
  uploadsToday.set(k, n);
  if (uploadsToday.size > 5000) uploadsToday.clear();
  return { url: saveImage(c.body.data) };
}, { big: true });
R('POST', '/api/my/orders/:id/transfer', 'customer', (c) => {
  const id = idOf(c);
  const o = get('SELECT * FROM orders WHERE id=? AND customer_id=?', id, c.cust.id);
  if (!o) throw notFound();
  if (o.paid || o.status === 'cancelled') throw bad('لا يمكن إضافة إثبات دفع لهذا الطلب');
  const ref = str(c.body.reference, 'رقم العملية', { max: 100 });
  const proof = c.body.proof || null;
  if (proof && !/^\/uploads\/[a-f0-9]{32}\.(jpg|png|webp)$/.test(proof)) throw bad('صورة غير صحيحة');
  if (!ref && !proof) throw bad('اكتب رقم العملية أو ارفع صورة التحويل');
  run("UPDATE orders SET payment='transfer', payment_ref=?, payment_proof=?, updated_at=? WHERE id=?", ref || null, proof, nowIso(), id);
  audit('customer:' + c.cust.phone, 'order.transfer-proof', '#' + id);
  return { ok: true };
});
R('POST', '/api/my/orders/:id/pay-card', 'customer', async (c) => {
  const cfg = paymobCfg();
  if (!cfg) throw bad('الدفع بالفيزا غير مفعّل حالياً');
  const id = idOf(c);
  const o = get('SELECT * FROM orders WHERE id=? AND customer_id=?', id, c.cust.id);
  if (!o) throw notFound();
  if (o.paid) throw bad('هذا الطلب مدفوع بالفعل');
  if (o.status === 'cancelled') throw bad('الطلب ملغي');
  const cents = Math.round(o.total * 100);
  if (!(cents > 0)) throw bad('مبلغ غير صحيح');
  const auth = await pmPost(cfg.base + '/api/auth/tokens', { api_key: cfg.key });
  const ord = await pmPost(cfg.base + '/api/ecommerce/orders', { auth_token: auth.token, delivery_needed: false, amount_cents: cents, currency: 'EGP', merchant_order_id: `KS${o.id}-${Date.now()}`, items: [] });
  const cu = c.cust, parts = String(cu.name).trim().split(/\s+/);
  const pk = await pmPost(cfg.base + '/api/acceptance/payment_keys', {
    auth_token: auth.token, amount_cents: cents, expiration: 3600, order_id: ord.id, currency: 'EGP', integration_id: Number(cfg.integration), lock_order_when_paid: true,
    billing_data: { first_name: parts[0] || 'NA', last_name: parts.slice(1).join(' ') || 'NA', email: cu.email || 'NA', phone_number: cu.phone, apartment: 'NA', floor: 'NA', street: o.address || 'NA', building: 'NA', shipping_method: 'NA', postal_code: 'NA', city: cu.city || 'NA', country: 'EG', state: 'NA' }
  });
  run("UPDATE orders SET payment='card', updated_at=? WHERE id=?", nowIso(), id);
  return { url: `${cfg.base}/api/acceptance/iframes/${cfg.iframe}?payment_token=${pk.token}` };
});
// Paymob server-to-server "transaction processed" callback. The ONLY thing that marks a card order paid. Verified by HMAC.
R('POST', '/api/paymob/callback', 'public', (c) => {
  const cfg = paymobCfg();
  if (!cfg) throw notFound();
  const obj = c.body && c.body.obj;
  if (!obj || !paymobHmacOk(obj, c.q.hmac, cfg.hmac)) { console.error('paymob callback: bad hmac'); throw new HttpError(401, 'invalid'); }
  const m = /^KS(\d+)-/.exec(String((obj.order && obj.order.merchant_order_id) || ''));
  if (!m) return { ok: true };
  const o = get('SELECT * FROM orders WHERE id=?', Number(m[1]));
  if (!o) return { ok: true };
  const good = truthy(obj.success) && !truthy(obj.pending) && !truthy(obj.is_voided) && !truthy(obj.is_refunded) && obj.currency === 'EGP' && Number(obj.amount_cents) === Math.round(o.total * 100);
  if (good && !o.paid) {
    run("UPDATE orders SET paid=1, payment='card', card_txn=?, paid_at=?, updated_at=? WHERE id=?", String(obj.id), nowIso(), nowIso(), o.id);
    audit('paymob', 'order.paid-card', `#${o.id} txn ${obj.id}`);
  } else if (!good) audit('paymob', 'callback.ignored', `#${o.id} success=${obj.success} amount=${obj.amount_cents}`);
  return { ok: true };
}, { noCsrf: true });

// --- staff & manager: session
R('GET', '/api/me', 'staff', (c) => ({ user: c.user, settings: { ...publicSettings(), staff_max_discount: Number(D.getSettings().staff_max_discount) } }));
R('POST', '/api/me/password', 'staff', (c) => {
  const u = get('SELECT * FROM users WHERE id=?', c.user.id);
  if (!checkPw(c.body.current_password, u.pass)) throw bad('كلمة السر الحالية غير صحيحة');
  run('UPDATE users SET pass=? WHERE id=?', hashPw(checkNewPw(c.body.new_password)), u.id);
  return { ok: true };
});

// --- products
R('GET', '/api/categories', 'staff', () => ({ items: categories() }));
R('GET', '/api/products/next-code', 'manager', (c) => {
  const cat = categories().find((x) => x.name === c.q.category);
  const prefix = cat ? cat.prefix : 'OT';
  const n = (get('SELECT value FROM counters WHERE key=?', 'code_' + prefix) || { value: 0 }).value + 1;
  return { code: `KS-${prefix}-${String(n).padStart(4, '0')}` };
});
R('GET', '/api/products/lookup/:code', 'staff', (c) => {
  const code = decodeURIComponent(c.p.code);
  const p = get('SELECT * FROM products WHERE active=1 AND (code=? OR barcode=?)', code, code);
  if (!p) throw notFound('المنتج غير موجود');
  return { product: productOut(p, c.user.role) };
});
R('GET', '/api/products', 'staff', (c) => {
  const params = [];
  const where = productFilters(c.q, params, { onlyActive: false });
  const { limit, offset } = paging(c.q);
  const rows = all(`SELECT * FROM products WHERE ${where} ORDER BY id DESC LIMIT ? OFFSET ?`, ...params, limit, offset);
  const total = get(`SELECT COUNT(*) n FROM products WHERE ${where}`, ...params).n;
  return { total, items: rows.map((p) => productOut(p, c.user.role)) };
});
R('POST', '/api/products', 'manager', (c) => {
  const b = c.body;
  const f = readProductBody(b, null);
  const stock = num(b.stock, 'الكمية', { int: true, max: 1e7, def: 0 });
  let code = str(b.code, 'الكود', { max: 30 });
  if (code && !/^[A-Za-z0-9\-_.]{2,30}$/.test(code)) throw bad('الكود: حروف إنجليزية وأرقام وشرطة فقط');
  try {
    const id = tx(() => {
      if (!code) code = nextCode(f.category);
      const now = nowIso();
      const r = run(`INSERT INTO products(code,barcode,name,name_en,category,description,color,material,cost,price_retail,price_semi,price_wholesale,stock,min_stock,images,active,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?)`, code, f.barcode, f.name, f.name_en, f.category, f.description, f.color, f.material, f.cost, f.price_retail, f.price_semi, f.price_wholesale, stock, f.min_stock, f.images, now, now);
      if (stock > 0) addMove(r.id, 'opening', stock, f.cost, 'رصيد افتتاحي', null, c.user.name);
      audit(c.user.name, 'product.create', code);
      return r.id;
    });
    return { product: productOut(get('SELECT * FROM products WHERE id=?', id), 'manager') };
  } catch (e) { throw uniqueErr(e, { 'products.code': 'هذا الكود مستخدم لمنتج آخر', 'products.barcode': 'هذا الباركود مستخدم لمنتج آخر' }); }
});
R('PATCH', '/api/products/:id', 'manager', (c) => {
  const id = idOf(c);
  const e = get('SELECT * FROM products WHERE id=?', id);
  if (!e) throw notFound();
  const f = readProductBody(c.body, e);
  const active = c.body.active !== undefined ? (c.body.active ? 1 : 0) : e.active;
  try {
    run(`UPDATE products SET barcode=?,name=?,name_en=?,category=?,description=?,color=?,material=?,cost=?,price_retail=?,price_semi=?,price_wholesale=?,min_stock=?,images=?,active=?,updated_at=? WHERE id=?`,
      f.barcode, f.name, f.name_en, f.category, f.description, f.color, f.material, f.cost, f.price_retail, f.price_semi, f.price_wholesale, f.min_stock, f.images, active, nowIso(), id);
  } catch (err) { throw uniqueErr(err, { 'products.barcode': 'هذا الباركود مستخدم لمنتج آخر' }); }
  const changed = ['cost', 'price_retail', 'price_semi', 'price_wholesale'].filter((k) => e[k] !== f[k]).map((k) => `${k}:${e[k]}→${f[k]}`);
  audit(c.user.name, 'product.update', `${e.code}${changed.length ? ' ' + changed.join(' ') : ''}`);
  return { product: productOut(get('SELECT * FROM products WHERE id=?', id), 'manager') };
});
R('POST', '/api/products/:id/stock', 'manager', (c) => {
  const id = idOf(c), b = c.body;
  const type = b.type;
  if (!['receive', 'adjust', 'damage'].includes(type)) throw bad('نوع الحركة غير صحيح');
  const qty = type === 'adjust' ? num(b.qty, 'الكمية', { min: -1e7, max: 1e7, int: true }) : num(b.qty, 'الكمية', { min: 1, max: 1e7, int: true });
  if (qty === 0) throw bad('الكمية يجب ألا تكون صفر');
  const signed = type === 'damage' ? -qty : qty;
  tx(() => {
    const p = get('SELECT * FROM products WHERE id=?', id);
    if (!p) throw notFound();
    if (p.stock + signed < 0) throw bad(`الرصيد لا يكفي (المتاح ${p.stock})`);
    let unitCost = null;
    if (type === 'receive') {
      unitCost = b.unit_cost !== undefined && b.unit_cost !== '' ? num(b.unit_cost, 'سعر الشراء', { max: 1e7 }) : p.cost;
      run('UPDATE products SET stock=stock+?, cost=?, updated_at=? WHERE id=?', signed, unitCost, nowIso(), id);
    } else run('UPDATE products SET stock=stock+?, updated_at=? WHERE id=?', signed, nowIso(), id);
    addMove(id, type, signed, unitCost, str(b.note, 'ملاحظة', { max: 200 }), null, c.user.name);
    audit(c.user.name, 'stock.' + type, `${p.code} ${signed > 0 ? '+' : ''}${signed}`);
  });
  return { product: productOut(get('SELECT * FROM products WHERE id=?', id), 'manager') };
});
R('GET', '/api/stock-moves', 'manager', (c) => {
  const params = [];
  let where = '1=1';
  if (c.q.product_id) { where += ' AND m.product_id=?'; params.push(Number(c.q.product_id)); }
  const { limit, offset } = paging(c.q);
  return { items: all(`SELECT m.*, p.code, p.name FROM stock_moves m JOIN products p ON p.id=m.product_id WHERE ${where} ORDER BY m.id DESC LIMIT ? OFFSET ?`, ...params, limit, offset) };
});
R('GET', '/api/inventory/summary', 'manager', () => {
  const t = get(`SELECT COUNT(*) products, COALESCE(SUM(stock),0) units, COALESCE(SUM(stock*cost),0) at_cost,
    COALESCE(SUM(stock*price_retail),0) at_retail, COALESCE(SUM(stock*(CASE WHEN price_wholesale>0 THEN price_wholesale ELSE price_retail END)),0) at_wholesale,
    COALESCE(SUM(CASE WHEN stock=0 THEN 1 ELSE 0 END),0) out_of_stock,
    COALESCE(SUM(CASE WHEN stock>0 AND stock<=min_stock THEN 1 ELSE 0 END),0) low FROM products WHERE active=1`);
  const lowList = all('SELECT id,code,name,category,stock,min_stock FROM products WHERE active=1 AND stock<=min_stock ORDER BY stock, name LIMIT 100');
  const byCat = all('SELECT category, COUNT(*) products, SUM(stock) units, SUM(stock*cost) at_cost FROM products WHERE active=1 GROUP BY category ORDER BY at_cost DESC');
  return { totals: { ...t, at_cost: round2(t.at_cost), at_retail: round2(t.at_retail), at_wholesale: round2(t.at_wholesale) }, low_stock: lowList, by_category: byCat.map((r) => ({ ...r, at_cost: round2(r.at_cost) })) };
});
R('POST', '/api/uploads', 'manager', (c) => ({ url: saveImage(c.body.data) }), { big: true });

// --- customers (staff + manager)
function customerWrite(c, existing) {
  const b = c.body, s = D.getSettings();
  const cap = c.user.role === 'manager' ? 100 : Number(s.staff_max_discount);
  const o = {};
  o.name = b.name !== undefined || !existing ? str(b.name, 'الاسم', { required: true, max: 80 }) : existing.name;
  o.phone = b.phone !== undefined || !existing ? normPhone(b.phone) : existing.phone;
  o.email = b.email !== undefined ? str(b.email, 'البريد', { max: 100 }) || null : existing ? existing.email : null;
  o.address = b.address !== undefined ? str(b.address, 'العنوان', { max: 300 }) : existing ? existing.address : '';
  o.city = b.city !== undefined ? str(b.city, 'المدينة', { max: 60 }) : existing ? existing.city : '';
  o.notes = b.notes !== undefined ? str(b.notes, 'ملاحظات', { max: 500 }) : existing ? existing.notes : '';
  o.tier = b.tier !== undefined ? b.tier : existing ? existing.tier : 'retail';
  if (!['retail', 'semi', 'wholesale'].includes(o.tier)) throw bad('فئة السعر غير صحيحة');
  o.discount_pct = b.discount_pct !== undefined ? num(b.discount_pct, 'نسبة الخصم', { max: 100 }) : existing ? existing.discount_pct : 0;
  if (o.discount_pct > cap) throw forbidden(`الحد الأقصى المسموح لك للخصم ${cap}%`);
  o.active = b.active !== undefined ? (b.active ? 1 : 0) : existing ? existing.active : 1;
  return o;
}
R('GET', '/api/customers', 'staff', (c) => {
  const params = [];
  let where = '1=1';
  if (c.q.q) { const l = likeEsc(String(c.q.q).slice(0, 60)); where += " AND (name LIKE ? ESCAPE '\\' OR phone LIKE ? ESCAPE '\\')"; params.push(l, l); }
  if (c.q.tier) { where += ' AND tier=?'; params.push(String(c.q.tier)); }
  const { limit, offset } = paging(c.q);
  const rows = all(`SELECT * FROM customers WHERE ${where} ORDER BY id DESC LIMIT ? OFFSET ?`, ...params, limit, offset);
  return { items: rows.map(customerOut) };
});
R('POST', '/api/customers', 'staff', (c) => {
  const o = customerWrite(c, null);
  let pass = null;
  if (c.body.password) pass = hashPw(checkNewPw(c.body.password));
  try {
    const id = run('INSERT INTO customers(name,phone,email,pass,tier,discount_pct,address,city,notes,active,created_at,created_by) VALUES(?,?,?,?,?,?,?,?,?,1,?,?)',
      o.name, o.phone, o.email, pass, o.tier, o.discount_pct, o.address, o.city, o.notes, nowIso(), c.user.name).id;
    audit(c.user.name, 'customer.create', `${o.name} ${o.tier} ${o.discount_pct}%`);
    return { customer: customerOut(get('SELECT * FROM customers WHERE id=?', id)) };
  } catch (e) { throw uniqueErr(e, { 'customers.phone': 'رقم الموبايل مسجل لعميل آخر' }); }
});
R('GET', '/api/customers/:id', 'staff', (c) => {
  const id = idOf(c);
  const cu = get('SELECT * FROM customers WHERE id=?', id);
  if (!cu) throw notFound();
  const orders = all('SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 50', id).filter((o) => staffCanSee(o, c.user));
  return { customer: customerOut(cu), stats: customerStats(id), orders: orders.map((o) => orderOut(o, c.user.role, false)) };
});
R('PATCH', '/api/customers/:id', 'staff', (c) => {
  const id = idOf(c);
  const ex = get('SELECT * FROM customers WHERE id=?', id);
  if (!ex) throw notFound();
  const o = customerWrite(c, ex);
  if (c.body.password) run('UPDATE customers SET pass=? WHERE id=?', hashPw(checkNewPw(c.body.password)), id);
  if (c.body.password || o.active === 0) run("DELETE FROM sessions WHERE kind='customer' AND uid=?", id);
  try {
    run('UPDATE customers SET name=?,phone=?,email=?,tier=?,discount_pct=?,address=?,city=?,notes=?,active=? WHERE id=?',
      o.name, o.phone, o.email, o.tier, o.discount_pct, o.address, o.city, o.notes, o.active, id);
  } catch (e) { throw uniqueErr(e, { 'customers.phone': 'رقم الموبايل مسجل لعميل آخر' }); }
  if (ex.discount_pct !== o.discount_pct || ex.tier !== o.tier) audit(c.user.name, 'customer.terms', `${ex.name} ${ex.tier}/${ex.discount_pct}% → ${o.tier}/${o.discount_pct}%`);
  return { customer: customerOut(get('SELECT * FROM customers WHERE id=?', id)) };
});

// --- orders (staff + manager)
R('GET', '/api/orders', 'staff', (c) => {
  const params = [];
  let where = '1=1';
  if (c.user.role !== 'manager') { where += " AND (channel='shop' OR created_by=?)"; params.push(c.user.id); }
  if (c.q.status) { where += ' AND status=?'; params.push(String(c.q.status)); }
  if (c.q.paid === '0' || c.q.paid === '1') { where += ' AND paid=?'; params.push(Number(c.q.paid)); }
  if (c.q.channel) { where += ' AND channel=?'; params.push(String(c.q.channel)); }
  if (c.q.customer_id) { where += ' AND customer_id=?'; params.push(Number(c.q.customer_id)); }
  if (c.q.from) { where += ' AND created_at>=?'; params.push(cairoStartUtc(c.q.from).toISOString()); }
  if (c.q.to) { where += ' AND created_at<?'; params.push(cairoStartUtc(addDay(c.q.to, 1)).toISOString()); }
  if (c.q.q) {
    const l = likeEsc(String(c.q.q).slice(0, 60));
    where += " AND (customer_name LIKE ? ESCAPE '\\' OR customer_phone LIKE ? ESCAPE '\\' OR CAST(id AS TEXT)=?)";
    params.push(l, l, String(c.q.q).trim());
  }
  const { limit, offset } = paging(c.q);
  const rows = all(`SELECT * FROM orders WHERE ${where} ORDER BY id DESC LIMIT ? OFFSET ?`, ...params, limit, offset);
  return { items: rows.map((o) => orderOut(o, c.user.role, false)) };
});
R('GET', '/api/orders/:id', 'staff', (c) => {
  const o = get('SELECT * FROM orders WHERE id=?', idOf(c));
  if (!o || !staffCanSee(o, c.user)) throw notFound('الطلب غير موجود');
  return { order: orderOut(o, c.user.role, true) };
});
R('POST', '/api/orders', 'staff', (c) => {
  const b = c.body, s = D.getSettings();
  let cust = null;
  if (b.customer_id) {
    cust = get('SELECT * FROM customers WHERE id=? AND active=1', Number(b.customer_id));
    if (!cust) throw bad('العميل غير موجود');
  }
  const tier = b.tier !== undefined ? b.tier : cust ? cust.tier : 'retail';
  if (!['retail', 'semi', 'wholesale'].includes(tier)) throw bad('فئة السعر غير صحيحة');
  const pct = b.discount_pct !== undefined && b.discount_pct !== '' ? num(b.discount_pct, 'نسبة الخصم', { max: 100 }) : cust ? cust.discount_pct : 0;
  const cap = c.user.role === 'manager' ? 100 : Number(s.staff_max_discount);
  if (pct > cap) throw forbidden(`الحد الأقصى المسموح لك للخصم ${cap}%`);
  const id = createOrder({
    items: b.items, customer: cust, channel: 'staff', tier, discountPct: pct,
    shipping: num(b.shipping, 'الشحن', { max: 1e6, def: 0 }), payment: str(b.payment, 'طريقة الدفع', { max: 40 }) || 'cash',
    note: str(b.note, 'ملاحظات', { max: 500 }), address: str(b.address, 'العنوان', { max: 300 }) || (cust && cust.address) || '',
    customerName: cust ? null : str(b.customer_name, 'اسم العميل', { max: 80 }) || null,
    customerPhone: cust ? null : str(b.customer_phone, 'الموبايل', { max: 30 }) || null,
    paid: !!b.paid, actor: c.user
  });
  audit(c.user.name, 'order.create', `#${id} ${tier} ${pct}%`);
  return { order: orderOut(get('SELECT * FROM orders WHERE id=?', id), c.user.role, true) };
});
R('POST', '/api/orders/:id/status', 'staff', (c) => {
  const id = idOf(c);
  const o = get('SELECT * FROM orders WHERE id=?', id);
  if (!o || !staffCanSee(o, c.user)) throw notFound('الطلب غير موجود');
  const to = String(c.body.status);
  if (!TRANSITIONS[o.status] || !['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'].includes(to)) throw bad('حالة غير صحيحة');
  return { order: orderOut(changeStatus(id, to, c.user), c.user.role, true) };
});
R('POST', '/api/orders/:id/paid', 'staff', (c) => {
  const id = idOf(c);
  const o = get('SELECT * FROM orders WHERE id=?', id);
  if (!o || !staffCanSee(o, c.user)) throw notFound('الطلب غير موجود');
  run('UPDATE orders SET paid=?, paid_at=?, updated_at=? WHERE id=?', c.body.paid ? 1 : 0, c.body.paid ? nowIso() : null, nowIso(), id);
  audit(c.user.name, 'order.paid', `#${id} ${c.body.paid ? 1 : 0}`);
  return { order: orderOut(get('SELECT * FROM orders WHERE id=?', id), c.user.role, true) };
});

// --- dashboard
R('GET', '/api/dashboard', 'staff', (c) => {
  const today = cairoDay(nowIso());
  const fromIso = cairoStartUtc(today).toISOString(), toIso = cairoStartUtc(addDay(today, 1)).toISOString();
  const pending = get("SELECT COUNT(*) n FROM orders WHERE status='pending'").n;
  const low = get('SELECT COUNT(*) n FROM products WHERE active=1 AND stock<=min_stock').n;
  if (c.user.role !== 'manager') {
    const mine = get(`SELECT COUNT(*) n, COALESCE(SUM(total),0) t FROM orders WHERE created_by=? AND status IN ${SALE_STATUSES} AND created_at>=? AND created_at<?`, c.user.id, fromIso, toIso);
    return { today: { orders: mine.n, sales: round2(mine.t) }, pending_orders: pending, low_stock: low };
  }
  const t = report(fromIso, toIso, true);
  const mFrom = cairoStartUtc(today.slice(0, 8) + '01').toISOString();
  const m = report(mFrom, toIso, true);
  const inv = get('SELECT COALESCE(SUM(stock*cost),0) v FROM products WHERE active=1').v;
  const unpaid = get(`SELECT COALESCE(SUM(total),0) v FROM orders WHERE paid=0 AND status IN ${SALE_STATUSES}`).v;
  return {
    today: { orders: t.orders, sales: t.sales, profit: t.profit }, month: { orders: m.orders, sales: m.sales, profit: m.profit },
    pending_orders: pending, low_stock: low, inventory_value: round2(inv), unpaid: round2(unpaid), top_products: m.top_products.slice(0, 5)
  };
});

// --- manager-only
R('GET', '/api/reports/summary', 'manager', (c) => {
  const r = rangeFromQuery(c.q, 30);
  return { from: r.from, to: r.to, ...report(r.fromIso, r.toIso, true) };
});
R('GET', '/api/staff', 'manager', () => ({ items: all('SELECT id,username,name,role,active,created_at FROM users ORDER BY id').map((u) => ({ ...u, active: !!u.active })) }));
R('POST', '/api/staff', 'manager', (c) => {
  const b = c.body;
  const username = str(b.username, 'اسم المستخدم', { required: true, max: 40 });
  if (!/^[A-Za-z0-9_.\-]{3,40}$/.test(username)) throw bad('اسم المستخدم: حروف إنجليزية وأرقام فقط (٣ أحرف على الأقل)');
  const role = b.role === 'manager' ? 'manager' : 'staff';
  try {
    const id = run('INSERT INTO users(username,name,role,pass,active,created_at) VALUES(?,?,?,?,1,?)', username, str(b.name, 'الاسم', { required: true, max: 80 }), role, hashPw(checkNewPw(b.password)), nowIso()).id;
    audit(c.user.name, 'staff.create', `${username} ${role}`);
    return { id };
  } catch (e) { throw uniqueErr(e, { 'users.username': 'اسم المستخدم موجود بالفعل' }); }
});
R('PATCH', '/api/staff/:id', 'manager', (c) => {
  const id = idOf(c), b = c.body;
  const u = get('SELECT * FROM users WHERE id=?', id);
  if (!u) throw notFound();
  const active = b.active !== undefined ? (b.active ? 1 : 0) : u.active;
  const role = b.role !== undefined ? (b.role === 'manager' ? 'manager' : 'staff') : u.role;
  if (u.id === c.user.id && (!active || role !== 'manager')) throw bad('لا يمكنك تعطيل نفسك أو إزالة صلاحية المدير عنك');
  run('UPDATE users SET name=?, active=?, role=? WHERE id=?', b.name !== undefined ? str(b.name, 'الاسم', { required: true, max: 80 }) : u.name, active, role, id);
  if (b.password) run('UPDATE users SET pass=? WHERE id=?', hashPw(checkNewPw(b.password)), id);
  if (b.password || !active || role !== u.role) run("DELETE FROM sessions WHERE kind='staff' AND uid=?", id);
  audit(c.user.name, 'staff.update', `${u.username}${b.password ? ' password' : ''}${active !== u.active ? ' active=' + active : ''}${role !== u.role ? ' role=' + role : ''}`);
  return { ok: true };
});
R('GET', '/api/settings', 'manager', () => {
  const s = D.getSettings();
  return { settings: { store_name: s.store_name, store_phone: s.store_phone, store_address: s.store_address, currency: s.currency, staff_max_discount: Number(s.staff_max_discount), default_min_stock: Number(s.default_min_stock), shipping_fee: Number(s.shipping_fee) || 0, bank_name: s.bank_name || '', bank_account_name: s.bank_account_name || '', bank_account_number: s.bank_account_number || '', bank_iban: s.bank_iban || '', wallet_number: s.wallet_number || '', instapay_handle: s.instapay_handle || '', payment_note: s.payment_note || '' }, categories: categories(), card_enabled: !!paymobCfg() };
});
R('PUT', '/api/settings', 'manager', (c) => {
  const b = c.body;
  for (const k of ['store_name', 'store_phone', 'store_address', 'currency']) if (b[k] !== undefined) D.setSetting(k, str(b[k], k, { required: k !== 'store_phone' && k !== 'store_address', max: 200 }));
  for (const k of ['bank_name', 'bank_account_name', 'bank_account_number', 'bank_iban', 'wallet_number', 'instapay_handle', 'payment_note']) if (b[k] !== undefined) D.setSetting(k, str(b[k], k, { max: 300 }));
  if (b.staff_max_discount !== undefined) D.setSetting('staff_max_discount', num(b.staff_max_discount, 'حد خصم الموظف', { max: 100 }));
  if (b.default_min_stock !== undefined) D.setSetting('default_min_stock', num(b.default_min_stock, 'حد التنبيه', { int: true, max: 1e6 }));
  if (b.shipping_fee !== undefined) D.setSetting('shipping_fee', num(b.shipping_fee, 'الشحن', { max: 1e6 }));
  if (b.categories !== undefined) {
    if (!Array.isArray(b.categories) || !b.categories.length || b.categories.length > 40) throw bad('الأقسام غير صحيحة');
    const seenN = new Set(), seenP = new Set();
    const cats = b.categories.map((x) => {
      const name = str(x.name, 'اسم القسم', { required: true, max: 60 });
      const prefix = str(x.prefix, 'رمز القسم', { required: true, max: 4 }).toUpperCase();
      if (!/^[A-Z0-9]{2,4}$/.test(prefix)) throw bad('رمز القسم: ٢–٤ حروف أو أرقام إنجليزية');
      if (seenN.has(name) || seenP.has(prefix)) throw bad('اسم أو رمز قسم مكرر');
      seenN.add(name); seenP.add(prefix);
      return { name, prefix };
    });
    D.setSetting('categories', JSON.stringify(cats));
  }
  audit(c.user.name, 'settings.update', Object.keys(b).join(','));
  return { ok: true };
});
R('GET', '/api/audit', 'manager', (c) => ({ items: all('SELECT * FROM audit ORDER BY id DESC LIMIT ?', paging(c.q).limit) }));
R('GET', '/api/backup', 'manager', (c) => {
  const f = path.join(D.DATA_DIR, `backup-${Date.now()}.db`);
  D.db.exec(`VACUUM INTO '${f.replace(/'/g, "''")}'`);
  const buf = fs.readFileSync(f);
  fs.unlinkSync(f);
  audit(c.user.name, 'backup', '');
  return { __raw: buf, type: 'application/octet-stream', filename: `karas-backup-${cairoDay(nowIso())}.db` };
});

/* ---------- dispatcher ---------- */
async function handle(c) {
  const { req } = c;
  const pathname = c.pathname;
  let matched = null, pathMatch = false;
  for (const r of routes) {
    const m = r.re.exec(pathname);
    if (!m) continue;
    pathMatch = true;
    if (r.method !== req.method) continue;
    matched = { r, m };
    break;
  }
  if (!matched) throw pathMatch ? new HttpError(405, 'طريقة غير مسموحة') : notFound('المسار غير موجود');
  const { r, m } = matched;
  if (req.method !== 'GET' && !r.noCsrf && req.headers['x-requested-with'] !== 'ks') throw forbidden('طلب غير مسموح');
  c.p = {};
  r.keys.forEach((k, i) => { c.p[k] = decodeURIComponent(m[i + 1]); });
  c.user = sessionUser(c, 'staff');
  c.cust = sessionUser(c, 'customer');
  if (r.auth === 'staff' || r.auth === 'manager') {
    if (!c.user) throw new HttpError(401, 'سجّل الدخول أولاً');
    if (r.auth === 'manager' && c.user.role !== 'manager') throw forbidden('هذه الصلاحية للمدير فقط');
  } else if (r.auth === 'customer' && !c.cust) throw new HttpError(401, 'سجّل الدخول أولاً');
  c.bodyLimit = r.big ? 6 * 1024 * 1024 : 256 * 1024;
  await c.readBody();
  return r.handler(c);
}

module.exports = { handle, HttpError };
