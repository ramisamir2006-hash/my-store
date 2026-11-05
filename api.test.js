'use strict';
// End-to-end API tests: starts the real server on a temp database.
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const assert = require('assert');

const PORT = 3100 + Math.floor(Math.random() * 500);
const DATA = fs.mkdtempSync(path.join(os.tmpdir(), 'karas-test-'));
const BASE = `http://127.0.0.1:${PORT}`;
const FAKE = PORT + 1000;
const crypto = require('crypto');
const http = require('http');

class Client {
  constructor() { this.jar = {}; }
  async call(method, url, body) {
    const headers = { 'X-Requested-With': 'ks' };
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    const ck = Object.entries(this.jar).map(([k, v]) => `${k}=${v}`).join('; ');
    if (ck) headers.Cookie = ck;
    const r = await fetch(BASE + url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    for (const sc of r.headers.getSetCookie()) {
      const [kv] = sc.split(';'); const i = kv.indexOf('=');
      const k = kv.slice(0, i), v = kv.slice(i + 1);
      if (/Max-Age=0/.test(sc)) delete this.jar[k]; else this.jar[k] = v;
    }
    let j = null; try { j = await r.json(); } catch (_) {}
    return { s: r.status, j };
  }
  get(u) { return this.call('GET', u); }
  post(u, b) { return this.call('POST', u, b || {}); }
  patch(u, b) { return this.call('PATCH', u, b || {}); }
  put(u, b) { return this.call('PUT', u, b || {}); }
}

let passed = 0;
const ok = (name, cond) => { assert.ok(cond, 'FAILED: ' + name); passed++; console.log('  ✓', name); };
const eq = (name, a, b) => { assert.deepStrictEqual(a, b, `FAILED: ${name} (got ${JSON.stringify(a)}, want ${JSON.stringify(b)})`); passed++; console.log('  ✓', name); };

async function main() {
  const fake = http.createServer((req, res) => {
    let b = ''; req.on('data', (d) => (b += d)); req.on('end', () => {
      res.setHeader('Content-Type', 'application/json');
      if (req.url === '/api/auth/tokens') return res.end(JSON.stringify({ token: 'AUTH' }));
      if (req.url === '/api/ecommerce/orders') return res.end(JSON.stringify({ id: 777 }));
      if (req.url === '/api/acceptance/payment_keys') return res.end(JSON.stringify({ token: 'PK' + JSON.parse(b).amount_cents }));
      res.statusCode = 404; res.end('{}');
    });
  }).listen(FAKE);
  const srv = spawn(process.execPath, ['--no-warnings', path.join(__dirname, '..', 'server', 'index.js')], { env: { ...process.env, PORT, DATA_DIR: DATA, PAYMOB_API_KEY: 'k', PAYMOB_INTEGRATION_ID: '123', PAYMOB_IFRAME_ID: 'IF1', PAYMOB_HMAC: 'testsecret', PAYMOB_BASE: `http://127.0.0.1:${FAKE}` }, stdio: ['ignore', 'pipe', 'inherit'] });
  try {
    for (let i = 0; i < 50; i++) { try { await fetch(BASE + '/api/health'); break; } catch (_) { await new Promise((r) => setTimeout(r, 100)); } }

    const png2 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
    const M = new Client(), S = new Client(), S2 = new Client(), C = new Client(), C2 = new Client(), anon = new Client();

    console.log('Setup & auth');
    eq('setup needed', (await anon.get('/api/setup/status')).j.needed, true);
    eq('products need login', (await anon.get('/api/products')).s, 401);
    eq('weak password refused', (await M.post('/api/setup', { name: 'Rami', username: 'rami', password: '123' })).s, 400);
    eq('setup manager', (await M.post('/api/setup', { name: 'Rami', username: 'rami', password: 'secret1' })).s, 200);
    eq('setup closed', (await anon.post('/api/setup', { name: 'x', username: 'hacker', password: 'secret1' })).s, 403);
    eq('manager me', (await M.get('/api/me')).j.user.role, 'manager');
    eq('csrf header required', (await fetch(BASE + '/api/auth/logout', { method: 'POST' })).status, 403);

    console.log('Staff accounts');
    eq('create staff', (await M.post('/api/staff', { username: 'ali', name: 'Ali', password: 'ali123' })).s, 200);
    eq('create staff 2', (await M.post('/api/staff', { username: 'omar', name: 'Omar', password: 'omar123' })).s, 200);
    eq('dup username', (await M.post('/api/staff', { username: 'ALI', name: 'x', password: 'ali123' })).s, 409);
    eq('wrong password', (await S.post('/api/auth/staff/login', { username: 'ali', password: 'bad' })).s, 401);
    eq('staff login', (await S.post('/api/auth/staff/login', { username: 'ali', password: 'ali123' })).s, 200);
    await S2.post('/api/auth/staff/login', { username: 'omar', password: 'omar123' });
    eq('staff role', (await S.get('/api/me')).j.user.role, 'staff');
    for (const [m, u] of [['get', '/api/staff'], ['get', '/api/reports/summary'], ['get', '/api/audit'], ['get', '/api/inventory/summary'], ['get', '/api/backup'], ['get', '/api/settings'], ['get', '/api/stock-moves']]) {
      eq(`staff blocked ${u}`, (await S[m](u)).s, 403);
    }
    eq('staff cannot create product', (await S.post('/api/products', { name: 'x', category: 'خواتم' })).s, 403);
    eq('staff cannot change settings', (await S.put('/api/settings', { staff_max_discount: 100 })).s, 403);

    console.log('Products, codes, prices');
    const p1 = (await M.post('/api/products', { name: 'خاتم ستانلس', category: 'خواتم', cost: 20, price_retail: 50, price_semi: 40, price_wholesale: 30, stock: 100, barcode: '6221234567890' })).j.product;
    eq('auto code', p1.code, 'KS-RG-0001');
    const p2 = (await M.post('/api/products', { name: 'سوار', category: 'أساور', cost: 30, price_retail: 80, price_semi: 65, price_wholesale: 50, stock: 10, min_stock: 3 })).j.product;
    eq('auto code per category', p2.code, 'KS-BR-0001');
    const p3 = (await M.post('/api/products', { name: 'خاتم تاني', category: 'خواتم', cost: 10, price_retail: 25, price_semi: 20, price_wholesale: 15, stock: 5 })).j.product;
    eq('code counter increments', p3.code, 'KS-RG-0002');
    eq('duplicate barcode refused', (await M.post('/api/products', { name: 'y', category: 'خواتم', barcode: '6221234567890' })).s, 409);
    eq('duplicate custom code refused', (await M.post('/api/products', { name: 'y', category: 'خواتم', code: 'ks-rg-0001' })).s, 409);
    eq('unknown category refused', (await M.post('/api/products', { name: 'y', category: 'nope' })).s, 400);
    eq('negative price refused', (await M.post('/api/products', { name: 'y', category: 'خواتم', price_retail: -1 })).s, 400);
    const sp = (await S.get('/api/products')).j.items;
    ok('staff list has no cost', sp.length === 3 && sp.every((p) => !('cost' in p)));
    ok('staff sees 3 prices', sp[0].price_wholesale > 0 && sp[0].price_semi > 0 && sp[0].price_retail > 0);
    ok('manager sees cost', (await M.get('/api/products')).j.items.every((p) => 'cost' in p));
    eq('lookup by barcode', (await S.get('/api/products/lookup/6221234567890')).j.product.code, 'KS-RG-0001');
    eq('lookup by code', (await S.get('/api/products/lookup/KS-BR-0001')).j.product.name, 'سوار');
    ok('lookup has no cost', !('cost' in (await S.get('/api/products/lookup/KS-BR-0001')).j.product));
    eq('search by name', (await S.get('/api/products?q=' + encodeURIComponent('سوار'))).j.items.length, 1);
    eq('search wildcard escaped', (await S.get('/api/products?q=%25')).j.items.length, 0);

    console.log('Stock');
    eq('receive stock', (await M.post(`/api/products/${p2.id}/stock`, { type: 'receive', qty: 20, unit_cost: 35 })).j.product.stock, 30);
    eq('receive updates cost', (await M.get('/api/products')).j.items.find((p) => p.id === p2.id).cost, 35);
    eq('damage', (await M.post(`/api/products/${p2.id}/stock`, { type: 'damage', qty: 2 })).j.product.stock, 28);
    eq('adjust negative', (await M.post(`/api/products/${p2.id}/stock`, { type: 'adjust', qty: -3 })).j.product.stock, 25);
    eq('cannot go below zero', (await M.post(`/api/products/${p2.id}/stock`, { type: 'damage', qty: 999 })).s, 400);
    eq('staff cannot move stock', (await S.post(`/api/products/${p2.id}/stock`, { type: 'receive', qty: 5 })).s, 403);
    eq('stock moves recorded', (await M.get(`/api/stock-moves?product_id=${p2.id}`)).j.items.length, 4);

    console.log('Customers & discounts');
    eq('staff cap default 100 ok', (await M.put('/api/settings', { staff_max_discount: 15 })).s, 200);
    const cw = (await S.post('/api/customers', { name: 'محل النور', phone: '01011112222', tier: 'wholesale', discount_pct: 10 })).j.customer;
    eq('staff creates customer with discount', cw.discount_pct, 10);
    eq('customer pass not leaked', 'pass' in cw, false);
    eq('staff discount above cap refused', (await S.patch(`/api/customers/${cw.id}`, { discount_pct: 20 })).s, 403);
    eq('staff discount within cap', (await S.patch(`/api/customers/${cw.id}`, { discount_pct: 12 })).j.customer.discount_pct, 12);
    eq('manager discount above staff cap', (await M.patch(`/api/customers/${cw.id}`, { discount_pct: 20 })).j.customer.discount_pct, 20);
    eq('dup phone', (await S.post('/api/customers', { name: 'x', phone: '01011112222' })).s, 409);
    eq('discount >100 refused', (await M.patch(`/api/customers/${cw.id}`, { discount_pct: 101 })).s, 400);
    await M.patch(`/api/customers/${cw.id}`, { discount_pct: 10 });

    console.log('Staff order (tier + discount + stock)');
    let o = (await S.post('/api/orders', { customer_id: cw.id, items: [{ product_id: p1.id, qty: 10 }, { code: 'KS-BR-0001', qty: 2 }] })).j.order;
    eq('wholesale unit price', o.items[0].unit_price, 30);
    eq('subtotal', o.subtotal, 30 * 10 + 50 * 2);
    eq('customer discount applied', o.discount_amount, 40);
    eq('total', o.total, 360);
    eq('staff order confirmed', o.status, 'confirmed');
    ok('staff order hides cost', o.items.every((i) => !('unit_cost' in i)) && !('profit' in o));
    eq('stock deducted', (await M.get('/api/products')).j.items.find((p) => p.id === p1.id).stock, 90);
    const mo = (await M.get(`/api/orders/${o.id}`)).j.order;
    eq('manager sees profit', mo.profit, (300 + 100 - 40) - (20 * 10 + 35 * 2));
    eq('discount override within cap', (await S.post('/api/orders', { customer_id: cw.id, discount_pct: 5, items: [{ product_id: p1.id, qty: 1 }] })).j.order.discount_pct, 5);
    eq('discount override above cap refused', (await S.post('/api/orders', { customer_id: cw.id, discount_pct: 16, items: [{ product_id: p1.id, qty: 1 }] })).s, 403);
    eq('manager override above cap', (await M.post('/api/orders', { customer_id: cw.id, discount_pct: 30, items: [{ product_id: p1.id, qty: 1 }] })).j.order.discount_pct, 30);
    eq('walk-in retail price', (await S.post('/api/orders', { customer_name: 'زبون', items: [{ product_id: p3.id, qty: 2 }] })).j.order.total, 50);
    eq('over stock refused', (await S.post('/api/orders', { items: [{ product_id: p3.id, qty: 999 }] })).s, 400);
    eq('empty order refused', (await S.post('/api/orders', { items: [] })).s, 400);
    eq('zero qty refused', (await S.post('/api/orders', { items: [{ product_id: p3.id, qty: 0 }] })).s, 400);
    eq('mark paid', (await S.post(`/api/orders/${o.id}/paid`, { paid: true })).j.order.paid, true);
    ok('staff2 cannot see staff1 order', (await S2.get(`/api/orders/${o.id}`)).s === 404);
    ok('staff2 list excludes it', !(await S2.get('/api/orders')).j.items.some((x) => x.id === o.id));
    eq('manager sees all', (await M.get('/api/orders')).j.items.length === 4, true);

    console.log('Cancel restores stock');
    const before = (await M.get('/api/products')).j.items.find((p) => p.id === p1.id).stock;
    eq('cancel confirmed', (await S.post(`/api/orders/${o.id}/status`, { status: 'cancelled' })).j.order.status, 'cancelled');
    eq('stock restored', (await M.get('/api/products')).j.items.find((p) => p.id === p1.id).stock, before + 10);
    eq('cannot re-cancel', (await S.post(`/api/orders/${o.id}/status`, { status: 'cancelled' })).s, 400);

    console.log('Customer app');
    eq('register', (await C.post('/api/auth/customer/register', { name: 'سارة', phone: '٠١٥٥٥٥٥٥٥٥٥', password: 'sara123' })).s, 200);
    eq('phone normalized', (await C.get('/api/my/me')).j.customer.phone, '01555555555');
    eq('register dup', (await anon.post('/api/auth/customer/register', { name: 'x', phone: '01555555555', password: 'sara123' })).s, 409);
    eq('cannot claim staff-made account', (await anon.post('/api/auth/customer/register', { name: 'x', phone: '01011112222', password: 'hack123' })).s, 409);
    eq('customer cannot use staff api', (await C.get('/api/products')).s, 401);
    eq('customer cannot see customers', (await C.get('/api/customers')).s, 401);
    const cat = (await C.get('/api/catalog')).j.items;
    ok('catalog has no cost / stock internals', cat.every((p) => !('cost' in p) && !('price_wholesale' in p) && !('min_stock' in p) && !('barcode' in p)));
    eq('retail customer sees retail price', cat.find((p) => p.id === p1.id).price, 50);
    eq('anon sees retail catalog', (await anon.get('/api/catalog')).j.items.find((p) => p.id === p1.id).price, 50);
    let co = (await C.post('/api/my/orders', { items: [{ product_id: p1.id, qty: 3 }], address: 'القاهرة' })).j.order;
    eq('customer order pending', co.status, 'pending');
    eq('customer order total', co.total, 150);
    const stockPre = (await M.get('/api/products')).j.items.find((p) => p.id === p1.id).stock;
    eq('customer needs address', (await C.post('/api/my/orders', { items: [{ product_id: p1.id, qty: 1 }], address: '' })).s, 400);
    // staff upgrades to wholesale + discount
    const sara = (await S.get('/api/customers?q=01555555555')).j.items[0];
    await S.patch(`/api/customers/${sara.id}`, { tier: 'wholesale', discount_pct: 10 });
    eq('customer sees new tier price', (await C.get('/api/catalog')).j.items.find((p) => p.id === p1.id).price, 30);
    eq('and final price', (await C.get('/api/catalog')).j.items.find((p) => p.id === p1.id).final_price, 27);
    eq('customer sees own orders only', (await C.get('/api/my/orders')).j.items.length, 1);
    await C2.post('/api/auth/customer/register', { name: 'منى', phone: '01666666666', password: 'mona123' });
    eq('other customer cannot see order', (await C2.get('/api/my/orders')).j.items.length, 0);
    eq('other customer cannot cancel', (await C2.post(`/api/my/orders/${co.id}/cancel`)).s, 404);
    ok('staff sees shop order', (await S2.get(`/api/orders/${co.id}`)).s === 200);
    eq('staff confirms -> stock deducted', (await S2.post(`/api/orders/${co.id}/status`, { status: 'confirmed' })).j.order.status, 'confirmed');
    eq('stock after confirm', (await M.get('/api/products')).j.items.find((p) => p.id === p1.id).stock, stockPre - 3);
    eq('customer cannot cancel confirmed', (await C.post(`/api/my/orders/${co.id}/cancel`)).s, 400);
    eq('staff cannot cancel delivered', (await (async () => {
      await S2.post(`/api/orders/${co.id}/status`, { status: 'delivered' });
      return (await S2.post(`/api/orders/${co.id}/status`, { status: 'cancelled' })).s;
    })()), 403);
    eq('manager can cancel delivered', (await M.post(`/api/orders/${co.id}/status`, { status: 'cancelled' })).s, 200);
    eq('stock restored by manager cancel', (await M.get('/api/products')).j.items.find((p) => p.id === p1.id).stock, stockPre);
    eq('wrong customer password', (await anon.post('/api/auth/customer/login', { phone: '01555555555', password: 'nope12' })).s, 401);
    eq('staff-made customer without password cannot log in', (await anon.post('/api/auth/customer/login', { phone: '01011112222', password: 'anything' })).s, 401);
    await S.patch(`/api/customers/${cw.id}`, { password: 'shop123' });
    eq('staff activates customer login', (await anon.post('/api/auth/customer/login', { phone: '01011112222', password: 'shop123' })).s, 200);


    console.log('Payments (bank transfer + card)');
    const pub0 = (await anon.get('/api/settings/public')).j.payment;
    eq('card enabled via env', pub0.card, true);
    eq('transfer not offered until bank details set', pub0.transfer, false);
    await M.post('/api/auth/staff/login', { username: 'rami', password: 'secret1' });
    eq('save bank details', (await M.put('/api/settings', { bank_name: 'بنك مصر', bank_account_name: 'كاراس', bank_account_number: '1234567890', wallet_number: '01010055855' })).s, 200);
    const pub1 = (await anon.get('/api/settings/public')).j.payment;
    ok('transfer offered with details', pub1.transfer && pub1.bank_name === 'بنك مصر' && pub1.wallet_number === '01010055855');
    ok('no secrets in public settings', !JSON.stringify(pub1).includes('testsecret'));
    const co2 = (await C.post('/api/my/orders', { items: [{ product_id: p1.id, qty: 2 }], address: 'القاهرة', payment: 'card' })).j.order;
    eq('card order total', co2.total, 54);
    const pk = await C.post(`/api/my/orders/${co2.id}/pay-card`);
    eq('pay-card ok', pk.s, 200);
    ok('pay-card url', pk.j.url.includes('/api/acceptance/iframes/IF1?payment_token=PK5400'));
    eq('other customer cannot pay my order', (await C2.post(`/api/my/orders/${co2.id}/pay-card`)).s, 404);
    const mk = (over) => ({ type: 'TRANSACTION', obj: { amount_cents: 5400, created_at: '2026-11-05T10:00:00', currency: 'EGP', error_occured: false, has_parent_transaction: false, id: 99001, integration_id: 123, is_3d_secure: true, is_auth: false, is_capture: false, is_refunded: false, is_standalone_payment: true, is_voided: false, order: { id: 777, merchant_order_id: `KS${co2.id}-1` }, owner: 5, pending: false, source_data: { pan: '2346', sub_type: 'MasterCard', type: 'card' }, success: true, ...over } });
    const F = ['amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction', 'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded', 'is_standalone_payment', 'is_voided', 'order.id', 'owner', 'pending', 'source_data.pan', 'source_data.sub_type', 'source_data.type', 'success'];
    const sign = (obj) => crypto.createHmac('sha512', 'testsecret').update(F.map((f) => String(f.split('.').reduce((a, k) => a[k], obj))).join('')).digest('hex');
    const cb = async (body, hmac) => fetch(`${BASE}/api/paymob/callback?hmac=${hmac}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const paidOf = async () => (await M.get(`/api/orders/${co2.id}`)).j.order.paid;
    eq('forged callback rejected', (await cb(mk({}), 'deadbeef')).status, 401);
    eq('not paid after forged', await paidOf(), false);
    const bad = mk({ amount_cents: 100 });
    eq('wrong amount accepted-but-ignored', (await cb(bad, sign(bad.obj))).status, 200);
    eq('not paid after wrong amount', await paidOf(), false);
    const failedTx = mk({ success: false });
    await cb(failedTx, sign(failedTx.obj));
    eq('not paid after failed tx', await paidOf(), false);
    const good = mk({});
    eq('valid callback', (await cb(good, sign(good.obj))).status, 200);
    eq('paid after valid callback', await paidOf(), true);
    eq('card txn stored', (await M.get(`/api/orders/${co2.id}`)).j.order.card_txn, '99001');
    eq('cannot pay twice', (await C.post(`/api/my/orders/${co2.id}/pay-card`)).s, 400);
    const co3 = (await C.post('/api/my/orders', { items: [{ product_id: p1.id, qty: 1 }], address: 'القاهرة', payment: 'transfer' })).j.order;
    eq('transfer needs ref or proof', (await C.post(`/api/my/orders/${co3.id}/transfer`, {})).s, 400);
    const upc = await C.post('/api/my/uploads', { data: png2 });
    eq('customer upload receipt', upc.s, 200);
    eq('anon cannot upload', (await new Client().post('/api/my/uploads', { data: png2 })).s, 401);
    eq('submit transfer proof', (await C.post(`/api/my/orders/${co3.id}/transfer`, { reference: 'TRX-555', proof: upc.j.url })).s, 200);
    const seen = (await S2.get(`/api/orders/${co3.id}`)).j.order;
    ok('staff sees transfer ref + proof', seen.payment_ref === 'TRX-555' && seen.payment_proof === upc.j.url && seen.paid === false);
    eq('staff confirms payment', (await S2.post(`/api/orders/${co3.id}/paid`, { paid: true })).j.order.paid, true);
    eq('proof url must be an upload', (await C.post(`/api/my/orders/${co3.id}/transfer`, { reference: 'x', proof: 'http://evil/x.png' })).s, 400);

    console.log('Reports & dashboard');
    const rep = (await M.get('/api/reports/summary')).j;
    ok('report has totals', rep.orders > 0 && rep.sales > 0 && typeof rep.profit === 'number');
    eq('report day grouping', rep.by_day.length >= 1, true);
    eq('staff dash no profit', 'profit' in (await S.get('/api/dashboard')).j.today, false);
    ok('manager dash has profit', 'profit' in (await M.get('/api/dashboard')).j.today);
    const inv = (await M.get('/api/inventory/summary')).j;
    ok('inventory summary', inv.totals.products === 3 && inv.totals.at_cost > 0 && inv.totals.at_retail > inv.totals.at_cost);
    eq('date range filter', (await M.get('/api/reports/summary?from=2020-01-01&to=2020-01-02')).j.orders, 0);
    eq('bad date refused', (await M.get('/api/reports/summary?from=garbage')).s, 400);

    console.log('Staff lifecycle & misc');
    const staffList = (await M.get('/api/staff')).j.items;
    const ali = staffList.find((u) => u.username === 'ali');
    eq('manager cannot disable self', (await M.patch(`/api/staff/${staffList[0].id}`, { active: false })).s, 400);
    await M.patch(`/api/staff/${ali.id}`, { active: false });
    eq('disabled staff session dies', (await S.get('/api/me')).s, 401);
    eq('disabled staff cannot login', (await S.post('/api/auth/staff/login', { username: 'ali', password: 'ali123' })).s, 401);
    ok('audit has entries', (await M.get('/api/audit')).j.items.length > 10);
    const bk = await fetch(BASE + '/api/backup', { headers: { Cookie: `ks_s=${M.jar.ks_s}` } });
    ok('backup is sqlite', Buffer.from(await bk.arrayBuffer()).slice(0, 15).toString() === 'SQLite format 3');
    eq('logout', (await M.post('/api/auth/logout')).s, 200);
    eq('after logout', (await M.get('/api/me')).s, 401);

    console.log('Uploads & static');
    const png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
    await M.post('/api/auth/staff/login', { username: 'rami', password: 'secret1' });
    const up = await M.post('/api/uploads', { data: png });
    eq('upload ok', up.s, 200);
    eq('uploaded file served', (await fetch(BASE + up.j.url)).status, 200);
    eq('fake image refused', (await M.post('/api/uploads', { data: 'data:image/png;base64,AAAAAAAA' })).s, 400);
    eq('script upload refused', (await M.post('/api/uploads', { data: 'data:text/html;base64,PHNjcmlwdD4=' })).s, 400);
    eq('path traversal blocked', (await fetch(BASE + '/..%2f..%2fetc/passwd')).status >= 400, true);
    eq('csp header', (await fetch(BASE + '/api/health')).headers.get('content-security-policy').includes("script-src 'self'"), true);

    console.log('\nALL ' + passed + ' CHECKS PASSED');
  } finally {
    srv.kill(); fake.close();
    fs.rmSync(DATA, { recursive: true, force: true });
  }
}
main().catch((e) => { console.error('\n' + (e.stack || e)); process.exit(1); });
