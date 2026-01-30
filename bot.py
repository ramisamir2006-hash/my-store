<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>متجر رامي سمير الذهبي</title>
    <style>
        :root { --main-gold: #D4AF37; --dark-bg: #1a1a1a; --text-white: #ffffff; }
        body { font-family: 'Cairo', sans-serif; background: var(--dark-bg); color: var(--text-white); margin: 0; padding-bottom: 80px; }
        .header { background: linear-gradient(45deg, #000, #444); padding: 20px; text-align: center; border-bottom: 2px solid var(--main-gold); }
        .category-bar { display: flex; overflow-x: auto; padding: 10px; gap: 10px; background: #222; sticky: top; z-index: 100; }
        .cat-btn { background: none; border: 1px solid var(--main-gold); color: gold; padding: 5px 15px; border-radius: 20px; white-space: nowrap; cursor: pointer; transition: 0.3s; }
        .cat-btn.active { background: var(--main-gold); color: black; }
        
        .products-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .product-card { background: #282828; border-radius: 12px; overflow: hidden; border: 1px solid #333; transition: 0.3s; }
        .product-img { width: 100%; height: 140px; object-fit: cover; background: #444; }
        .product-info { padding: 10px; text-align: center; }
        .product-name { font-size: 0.9em; height: 2.4em; overflow: hidden; margin-bottom: 5px; }
        .price { color: var(--main-gold); font-weight: bold; font-size: 1.1em; }
        
        .size-selector { width: 100%; margin: 8px 0; background: #333; color: gold; border: 1px solid #444; border-radius: 5px; font-size: 0.8em; padding: 3px; }
        .buy-btn { background: var(--main-gold); border: none; width: 100%; padding: 10px; font-weight: bold; cursor: pointer; border-radius: 5px; }

        .cart-panel, .admin-panel { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--dark-bg); z-index: 1000; display: none; overflow-y: auto; padding: 20px; box-sizing: border-box; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: gold; font-size: 0.9em; }
        input, select, textarea { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #222; color: #fff; box-sizing: border-box; }
        
        .footer-nav { position: fixed; bottom: 0; width: 100%; background: #000; display: flex; justify-content: space-around; padding: 12px 0; border-top: 2px solid var(--main-gold); z-index: 999; }
        .nav-item { color: #fff; text-decoration: none; font-size: 0.85em; text-align: center; cursor: pointer; opacity: 0.7; }
        .nav-item:hover { opacity: 1; color: var(--main-gold); }

        .preview-imgs-scroll { display: flex; overflow-x: auto; gap: 8px; margin: 10px 0; }
        .preview-img-item { width: 70px; height: 70px; border-radius: 8px; object-fit: cover; border: 1.5px solid var(--main-gold); }
    </style>
</head>
<body>

<div class="header">
    <h2>✨ مـجـوهرات رامـي سـمـيـر ✨</h2>
    <div id="userTypeBadge" style="color: gold; font-size: 0.8em; letter-spacing: 1px;">أفخم الموديلات العالمية بين يديك</div>
</div>

<div class="category-bar" id="cats">
    <button class="cat-btn active" onclick="filterProducts('الكل', this)">الكل</button>
    <button class="cat-btn" onclick="filterProducts('غوايش', this)">غوايش</button>
    <button class="cat-btn" onclick="filterProducts('خواتم', this)">خواتم</button>
    <button class="cat-btn" onclick="filterProducts('سلاسل', this)">سلاسل</button>
</div>

<div class="products-grid" id="mainGrid"></div>

<div id="adminPanel" class="admin-panel">
    <h3 style="color: gold; text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;">🛡️ إضافة منتج جديد للقناة والمتجر</h3>
    
    <div class="form-group">
        <label>📸 روابط الصور (كل رابط في سطر - حتى 10):</label>
        <textarea id="p_imgs" placeholder="ضع روابط الصور هنا..." rows="4" oninput="updatePreview()"></textarea>
    </div>

    <div class="form-group">
        <label>💎 اسم الموديل:</label>
        <input type="text" id="p_name" placeholder="اسم القطعة.." oninput="updatePreview()">
    </div>

    <div class="form-group">
        <label>📂 القسم:</label>
        <select id="p_cat" onchange="updatePreview()">
            <option value="غوايش">غوايش</option>
            <option value="خواتم">خواتم</option>
            <option value="سلاسل">سلاسل</option>
        </select>
    </div>

    <div class="form-group">
        <label>📝 وصف المنتج:</label>
        <textarea id="p_desc" placeholder="وصف يجذب الزبائن.." oninput="updatePreview()"></textarea>
    </div>

    <div class="form-group">
        <label>💰 السعر:</label>
        <input type="number" id="p_price" placeholder="0.00" oninput="updatePreview()">
    </div>

    <div class="form-group">
        <label>📏 المقاسات المتاحة:</label>
        <input type="text" id="p_sizes" placeholder="مثلاً: 18, 19, 20" oninput="updatePreview()">
    </div>

    <div id="previewArea" style="background: #222; padding: 15px; border-radius: 12px; border: 1px solid var(--main-gold); margin-bottom: 20px;">
        <p style="font-size: 0.75em; color: var(--main-gold); margin-top: 0;">👁️ معاينة العرض:</p>
        <div id="previewContent"></div>
    </div>

    <button class="buy-btn" onclick="saveAndPublish()">🚀 حفظ المنتج ونشره بالقناة</button>
    <button class="buy-btn" style="background: #333; margin-top: 10px;" onclick="closePanels()">إلغاء</button>
</div>

<div id="cartPanel" class="cart-panel">
    <h3>🛒 تأكيد الطلب</h3>
    <div id="cartItemsList"></div>
    <hr style="border: 0.5px solid #333;">
    <div class="form-group"><input type="text" id="cust_name" placeholder="الاسم الكامل"></div>
    <div class="form-group"><input type="tel" id="cust_phone" placeholder="رقم الموبايل"></div>
    <div class="form-group"><textarea id="cust_addr" placeholder="العنوان بالتفصيل"></textarea></div>
    <div class="form-group">
        <label>طريقة الاستلام:</label>
        <select id="ship_type">
            <option value="delivery">توصيل للمنزل</option>
            <option value="pickup">استلام من الفرع</option>
        </select>
    </div>
    <div id="orderSummary" style="margin: 15px 0; font-weight: bold; color: gold;"></div>
    <button class="buy-btn" style="background: #28a745;" onclick="confirmOrder()">إرسال الطلب عبر الواتساب/البوت 🚀</button>
    <button class="buy-btn" style="background: #444; margin-top: 10px;" onclick="closePanels()">رجوع</button>
</div>

<div class="footer-nav">
    <div class="nav-item" onclick="showPanel('main')">🏠 المتجر</div>
    <div class="nav-item" onclick="showPanel('cart')">🛒 السلة (<span id="cartCount">0</span>)</div>
    <div class="nav-item" id="adminTab" onclick="showPanel('admin')" style="display: none;">⚙️ الإدارة</div>
</div>

<script>
    let tg = window.Telegram.WebApp;
    tg.expand();

    const ADMIN_ID = 7020070481;
    if(tg.initDataUnsafe.user?.id === ADMIN_ID) document.getElementById('adminTab').style.display = 'block';

    let cart = [];
    let products = JSON.parse(localStorage.getItem('ramy_gold_db')) || [];

    function renderProducts(filter = 'الكل') {
        let html = '';
        let filtered = filter === 'الكل' ? products : products.filter(p => p.cat === filter);
        
        if(filtered.length === 0) {
            html = '<p style="text-align:center; padding:20px; color:#777;">لا يوجد منتجات في هذا القسم حالياً.</p>';
        } else {
            filtered.forEach(p => {
                html += `
                    <div class="product-card">
                        <img src="${p.imgs[0] || ''}" class="product-img" onerror="this.src='https://via.placeholder.com/150/222/gold?text=Ramy+Gold'">
                        <div class="product-info">
                            <div class="product-name">${p.name}</div>
                            <div class="price">${p.price} ج.م</div>
                            <select class="size-selector" id="size_${p.id}">
                                ${p.sizes.split(',').map(s => `<option>${s.trim()}</option>`).join('')}
                            </select>
                            <button class="buy-btn" onclick="addToCart(${p.id})">شراء 🛒</button>
                        </div>
                    </div>
                `;
            });
        }
        document.getElementById('mainGrid').innerHTML = html;
    }

    function filterProducts(cat, btn) {
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderProducts(cat);
    }

    function updatePreview() {
        let name = document.getElementById('p_name').value || "اسم المنتج";
        let price = document.getElementById('p_price').value || "0";
        let imgs = document.getElementById('p_imgs').value.split('\n').filter(u => u.trim() !== "");
        
        let imgHtml = '<div class="preview-imgs-scroll">';
        imgs.forEach(url => imgHtml += `<img src="${url}" class="preview-img-item">`);
        imgHtml += '</div>';

        document.getElementById('previewContent').innerHTML = `
            ${imgHtml}
            <div style="color:white; font-weight:bold;">${name}</div>
            <div style="color:gold;">السعر: ${price} ج.م</div>
        `;
    }

    function saveAndPublish() {
        let newP = {
            id: Date.now(),
            name: document.getElementById('p_name').value,
            price: document.getElementById('p_price').value,
            cat: document.getElementById('p_cat').value,
            desc: document.getElementById('p_desc').value,
            sizes: document.getElementById('p_sizes').value,
            imgs: document.getElementById('p_imgs').value.split('\n').filter(u => u.trim() !== "")
        };

        if(!newP.name || !newP.price) return tg.showAlert("أكمل البيانات أولاً");

        products.push(newP);
        localStorage.setItem('ramy_gold_db', JSON.stringify(products));
        
        // إرسال للبوت للنشر في القناة
        tg.sendData(JSON.stringify({action: "publish", ...newP}));
        
        tg.showPopup({message: "تم الحفظ بنجاح!"});
        renderProducts();
        closePanels();
    }

    function addToCart(id) {
        let p = products.find(x => x.id === id);
        let size = document.getElementById('size_'+id).value;
        cart.push({...p, selectedSize: size});
        document.getElementById('cartCount').innerText = cart.length;
        tg.showPopup({message: "تمت الإضافة للسلة ✅"});
    }

    function showPanel(p) {
        closePanels();
        if(p === 'admin') document.getElementById('adminPanel').style.display = 'block';
        if(p === 'cart') {
            document.getElementById('cartPanel').style.display = 'block';
            let total = cart.reduce((s, i) => s + parseFloat(i.price), 0);
            document.getElementById('orderSummary').innerText = "إجمالي الطلب: " + total + " ج.م";
        }
    }

    function closePanels() {
        document.getElementById('adminPanel').style.display = 'none';
        document.getElementById('cartPanel').style.display = 'none';
    }

    function confirmOrder() {
        if(cart.length === 0) return tg.showAlert("السلة فارغة!");
        let data = {
            customer: document.getElementById('cust_name').value,
            phone: document.getElementById('cust_phone').value,
            address: document.getElementById('cust_addr').value,
            items: cart
        };
        tg.sendData(JSON.stringify({action: "order", ...data}));
        tg.close();
    }

    renderProducts();
</script>
</body>
</html>
