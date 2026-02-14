$(document).ready(function() {
    
    // وظيفة حفظ المنتج في قاعدة البيانات
    $(document).on('click', '#btnAddProduct', function() {
        let data = {
            action: 'add_product',
            pName: $('#prodTitle').val(),
            pCat: $('#prodCat').val(),
            pShip: $('#shippingMethod').val()
        };

        $.post('process.php', data, function(response) {
            if(response === "success") {
                alert("تم الحفظ في قاعدة البيانات بنجاح!");
                loadProducts(); // تحديث القائمة فوراً
            }
        });
    });

    // وظيفة جلب البيانات من القاعدة عند تحميل الصفحة
    function loadProducts() {
        $.getJSON('process.php?action=get_products', function(data) {
            let html = data.map(p => `
                <div class="product-item">
                    <div><strong>${p.product_name}</strong><br><small>${p.shipping_method}</small></div>
                    <div class="status-tag">${p.status}</div>
                </div>
            `).join('');
            $('#productListContainer').html(html);
        });
    }

    loadProducts(); // استدعاء الجلب عند فتح الصفحة
});
