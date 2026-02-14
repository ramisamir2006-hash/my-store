$(document).ready(function() {
    // مصفوفات البيانات (Database Simulation)
    let categories = ["إلكترونيات", "أزياء", "أدوات منزلية"];
    let warehouseProducts = [];

    // --- وظائف التنقل ---

    // 1. نموذج تسجيل التاجر
    $("#showVendorReg").click(function() {
        $("#dynamicForm").html(`
            <h3>تسجيل تاجر جديد في سوق مصر</h3>
            <div class="form-group">
                <label>اسم المتجر/التاجر</label>
                <input type="text" id="vName" placeholder="مثلاً: شركة النور للتجارة">
            </div>
            <div class="form-group">
                <label>رقم التواصل (واتساب)</label>
                <input type="text" id="vPhone" placeholder="010xxxxxxx">
            </div>
            <div class="form-group">
                <label>تخصص التجارة</label>
                <select id="vSpec">${categories.map(c => `<option>${c}</option>`).join('')}</select>
            </div>
            <button class="btn-submit" id="btnRegisterVendor">فتح حساب تاجر</button>
        `);
    });

    // 2. نموذج إضافة قسم جديد
    $("#showAddDept").click(function() {
        $("#dynamicForm").html(`
            <h3>إضافة مجال/قسم جديد للمنصة</h3>
            <div class="form-group">
                <label>اسم القسم الجديد</label>
                <input type="text" id="inputDeptName" placeholder="أدخل القسم هنا">
            </div>
            <button class="btn-submit" id="btnSaveDept">اعتماد القسم في النظام</button>
        `);
    });

    // 3. نموذج إضافة منتج للمستودع
    $("#showAddProduct").click(function() {
        let catOptions = categories.map(c => `<option value="${c}">${c}</option>`).join('');
        $("#dynamicForm").html(`
            <h3>إضافة منتجات للمستودع</h3>
            <div class="form-group">
                <label>اسم المنتج</label>
                <input type="text" id="prodTitle">
            </div>
            <div class="form-group">
                <label>القسم</label>
                <select id="prodCat">${catOptions}</select>
            </div>
            <div class="form-group">
                <label>طريقة الشحن والاستلام</label>
                <select id="shippingMethod">
                    <option>شحن سريع (القاهرة والجيزة)</option>
                    <option>شحن محافظات (3 أيام)</option>
                    <option>استلام من مستودع المنصة</option>
                </select>
            </div>
            <button class="btn-submit" id="btnAddProduct">تأذين الدخول للمستودع</button>
        `);
    });

    // --- معالجة العمليات (Logic) ---

    // حفظ القسم
    $(document).on('click', '#btnSaveDept', function() {
        let name = $('#inputDeptName').val();
        if(name) {
            categories.push(name);
            alert("تم إضافة قسم " + name + " لجميع التجار.");
            $('#inputDeptName').val('');
        }
    });

    // تسجيل التاجر
    $(document).on('click', '#btnRegisterVendor', function() {
        let vName = $('#vName').val();
        if(vName) {
            alert("تم تسجيل " + vName + " بنجاح. تم تفعيل المستودع الخاص بالتاجر.");
        }
    });

    // إضافة منتج وعرضه
    $(document).on('click', '#btnAddProduct', function() {
        let title = $('#prodTitle').val();
        let method = $('#shippingMethod').val();
        if(title) {
            let p = { id: Date.now(), title: title, method: method, status: "في الانتظار" };
            warehouseProducts.push(p);
            renderProducts();
            alert("تم إرسال تقرير للمشرف: منتج جديد دخل المستودع.");
            $('#prodTitle').val('');
        }
    });

    function renderProducts() {
        if(warehouseProducts.length === 0) return;
        $(".empty-msg").hide();
        let html = warehouseProducts.map(p => `
            <div class="product-item">
                <div>
                    <strong>${p.title}</strong><br>
                    <small>النظام: ${p.method}</small>
                </div>
                <div class="status-tag">${p.status}</div>
            </div>
        `).join('');
        $('#productListContainer').html(html);
    }
});
