from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpRequest, HttpResponse, Http404
from .models import Order, GroupPurchase
from .forms import OrderForm
from products.models import Product
from django.contrib import messages
from django.db.models import Count
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db import transaction


def check_group_purchase_availability(group_purchase, product):
    """التحقق من أن غرفة الشراء الجماعي لا تزال مفتوحة ومتاحة"""
    cache_key = f"group_purchase_{group_purchase.id}_availability"
    is_available = cache.get(cache_key)
    
    if is_available is None:
        is_available = product.quantity > 0 and group_purchase.participants.count() < product.max_participants
        cache.set(cache_key, is_available, timeout=60)  # تخزين النتيجة لمدة 60 ثانية
    
    if not is_available:
        group_purchase.is_active = False
        group_purchase.save()
    
    return is_available



def create_order_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # تحقق من الكمية المتاحة للمنتج
    if product.quantity <= 0:
        messages.error(request, "Sorry, the product is out of stock", "alert-danger")
        return redirect('products:product_detail_view', product_id=product.id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.product = product
                order.order_type = Order.OrderType.INDIVIDUAL
                order.participants = 1
                order.save()
                messages.success(request, "تم إنشاء الطلب الفردي بنجاح!")
                return redirect('orders:order_detail', order_id=order.id)  # توجيه المستخدم إلى تفاصيل الطلب
        else:
            messages.error(request, "حدث خطأ أثناء إنشاء الطلب.")
    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form, 'product': product})



def create_group_purchase(request, product_id):
    """إنشاء غرفة شراء جماعي وإعادة التوجيه إلى تفاصيلها"""
    product = get_object_or_404(Product, id=product_id)

    # التحقق من أن المنتج يحتوي على الكمية المتاحة
    if product.quantity <= 0:
        messages.error(request, "Unable to create a group purchase room. The product is out of stock in Database", "alert-danger")
        return redirect('products:product_detail_view', product_id=product.id)

    # استخدام معاملة لضمان صحة العملية
    if request.method == 'POST':
        with transaction.atomic():
            # التحقق من الكمية المتاحة في إطار المعاملة
            if product.quantity > 0:
                # إنشاء غرفة الشراء الجماعي
                group_purchase = GroupPurchase.objects.create(product=product)
                messages.success(request, "تم إنشاء غرفة الشراء الجماعي بنجاح!")

                # إنشاء الرابط الخاص للغرفة
                group_purchase_link = request.build_absolute_uri(
                    reverse('orders:group_purchase_detail', args=[group_purchase.id])
                )

                return render(request, 'orders/group_purchase_detail.html', {
                    'group_purchase': group_purchase,
                    'group_purchase_link': group_purchase_link,
                })
            else:
                messages.error(request, "المنتج لا يحتوي على الكمية الكافية لإنشاء غرفة شراء جماعي.", "alert-danger")
                return redirect('products:product_detail_view', product_id=product.id)

    return render(request, 'orders/create_group_purchase.html', {'product': product})

def join_group_purchase(request, group_purchase_id):
    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
    product = group_purchase.product
    
    if not check_group_purchase_availability(group_purchase, product):
        messages.error(request, "عذرًا، هذا المنتج غير متوفر حاليًا أو تم الوصول للحد الأقصى من المشاركين!")
        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
    
    if request.user in group_purchase.participants.all():
        messages.warning(request, "أنت بالفعل مشارك في هذا الشراء الجماعي!")
    else:
        with transaction.atomic():
            group_purchase.add_participant(request.user)
            product.quantity -= 1
            product.save()
            messages.success(request, "تم الانضمام إلى الشراء الجماعي بنجاح!")
        
        if group_purchase.participants.count() >= product.max_participants or product.quantity <= 0:
            group_purchase.is_active = False
            group_purchase.save()
    
    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)


def group_purchase_detail(request, group_purchase_id):
    """عرض تفاصيل غرفة الشراء الجماعي"""
    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
    return render(request, 'orders/group_purchase_detail.html', {'group_purchase': group_purchase})

def create_order_in_group(request, group_purchase_id):
    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
    
    if not group_purchase.is_active:
        messages.error(request, "هذا الشراء الجماعي مغلق!")
        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "الكمية غير صحيحة!")
            return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
        
        price = group_purchase.product.group_price or group_purchase.product.price
        total_price = quantity * price
        
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                product=group_purchase.product,
                quantity=quantity,
                total_price=total_price,
                order_type=Order.OrderType.GROUP,
                group_purchase=group_purchase
            )
            group_purchase.add_participant(request.user)
            messages.success(request, "تم إنشاء طلبك في الشراء الجماعي بنجاح!")
        
        return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/create_order_in_group.html', {'group_purchase': group_purchase})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})


# this is working 
#from django.shortcuts import render, redirect, get_object_or_404, reverse
#from django.http import HttpRequest, HttpResponse, Http404
#from .models import Order, GroupPurchase
#from .forms import OrderForm
#from products.models import Product
#from django.contrib import messages
#from django.db.models import Count
#from django.core.cache import cache
#from django.contrib.auth.models import User
#
## إنشاء دالة مساعدة للتحقق من الشروط المشتركة لغرف الشراء الجماعي
#def check_group_purchase_availability(group_purchase, product):
#    """التحقق من أن غرفة الشراء الجماعي مفتوحة ومتاح لها المشاركين."""
#    if product.quantity <= 0 or group_purchase.participants.count() >= product.max_participants:
#        group_purchase.is_active = False
#        group_purchase.save()
#        return False
#    return True
#
#def create_order_view(request, product_id):
#    product = get_object_or_404(Product, id=product_id)
#
#    if request.method == 'POST':
#        form = OrderForm(request.POST)
#        if form.is_valid():
#            order = form.save(commit=False)
#            order.user = request.user
#            order.product = product
#            order.order_type = Order.OrderType.INDIVIDUAL
#            order.participants = 1
#            order.save()
#            messages.success(request, "Individual order created successfully!")
#            return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#        else:
#            messages.error(request, "An error occurred while creating the request.")
#            return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#    else:
#        form = OrderForm()
#
#    return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#def create_group_purchase(request, product_id):
#    """إنشاء غرفة شراء جماعي وإعادة التوجيه إلى تفاصيلها"""
#    product = get_object_or_404(Product, id=product_id)
#        # تحقق إذا كان المنتج يحتوي على سعر خصم
#    if not product.group_price:  # إذا لم يكن هناك سعر خصم
#        messages.error(request, "نعتذر، هذا المنتج لا يحتوي على خصم لبدء شراء جماعي.", "alert-danger")
#        return redirect('products:product_detail_view', product_id=product.id)
#
#    if request.method == 'POST':
#        group_purchase = GroupPurchase.objects.create(product=product)
#        messages.success(request, "Group buying room created successfully!")
#
#        # إنشاء الرابط الخاص للغرفة
#        group_purchase_link = request.build_absolute_uri(
#            reverse('orders:group_purchase_detail', args=[group_purchase.id])
#        )
#
#        return render(request, 'orders/group_purchase_detail.html', {
#            'group_purchase': group_purchase,
#            'group_purchase_link': group_purchase_link,
#        })
#
#    return render(request, 'orders/create_group_purchase.html', {'product': product})
#
#def group_purchase_detail(request, group_purchase_id):
#    """عرض تفاصيل غرفة الشراء الجماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    return render(request, 'orders/group_purchase_detail.html', {'group_purchase': group_purchase})
#
#
#def join_group_purchase(request, group_purchase_id):
#    """الانضمام إلى الشراء الجماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    product = group_purchase.product
#    
#    if not check_group_purchase_availability(group_purchase, product):
#        messages.error(request, "عذرًا، هذا المنتج غير متوفر حاليًا أو تم الوصول للحد الأقصى من المشاركين!","alert-danger")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    if request.user.is_authenticated:
#        if request.user not in group_purchase.participants.all():
#            group_purchase.add_participant(request.user)
#            product.quantity -= 1
#            product.save()
#            messages.success(request, "تم الانضمام إلى الشراء الجماعي بنجاح!", "alert-success")
#
#            if group_purchase.participants.count() >= product.max_participants or product.quantity <= 0:
#                group_purchase.is_active = False
#                group_purchase.save()
#        else:
#            messages.warning(request, "أنت بالفعل مشارك في هذا الشراء الجماعي!")
#    else:
#        messages.error(request, "يجب عليك تسجيل الدخول للانضمام إلى الشراء الجماعي!", "alert-danger")
#
#    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#
#def create_order_in_group(request, group_purchase_id):
#    """إنشاء طلب داخل غرفة شراء جماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#
#    if not group_purchase.is_active:
#        messages.error(request, "هذا الشراء الجماعي مغلق!")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    if request.method == 'POST':
#        quantity = int(request.POST.get('quantity', 1))
#        price = group_purchase.product.group_price if group_purchase.product.group_price else group_purchase.product.price
#        total_price = quantity * price
#
#        order = Order.objects.create(
#            user=request.user,
#            product=group_purchase.product,
#            quantity=quantity,
#            total_price=total_price,
#            order_type=Order.OrderType.GROUP,
#            group_purchase=group_purchase
#        )
#
#        group_purchase.add_participant(request.user)
#
#        messages.success(request, "تم إنشاء طلبك في الشراء الجماعي بنجاح!")
#        return redirect('orders:order_detail', order_id=order.id)
#
#    return render(request, 'orders/create_order_in_group.html', {'group_purchase': group_purchase})
#
#def order_detail(request, order_id):
#    """عرض تفاصيل الطلب"""
#    order = get_object_or_404(Order, id=order_id)
#    return render(request, 'orders/order_detail.html', {'order': order})
#
#
#def join_group_purchase(request, group_purchase_id):
#    """الانضمام إلى الشراء الجماعي مع استخدام الكوكيز"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    product = group_purchase.product
#
#    # مفتاح الكوكيز لهذا الشراء الجماعي
#    cookie_key = f"group_purchase_{group_purchase_id}"
#    participants = request.COOKIES.get(cookie_key, "")  # استرجاع المشاركين
#
#    print(f"📝 المشاركون في الكوكيز قبل الإضافة: {participants}")  # 🔍 تتبع القيم الحالية
#
#    # تحويل المشاركين إلى قائمة وإزالة الفراغات
#    participants_list = [p for p in participants.split(",") if p]  
#
#    if str(request.user.id) in participants_list:
#        messages.warning(request, "أنت بالفعل مشارك في هذا الشراء الجماعي!")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    if not check_group_purchase_availability(group_purchase, product):
#        messages.error(request, "عذرًا، هذا المنتج غير متوفر حاليًا أو تم الوصول للحد الأقصى من المشاركين!", "alert-danger")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    if request.user.is_authenticated:
#        # إضافة المستخدم الجديد إلى القائمة وتحديث الكوكيز
#        participants_list.append(str(request.user.id))
#        new_participants = ",".join(participants_list)  
#
#        print(f"✅ بعد الإضافة: {new_participants}")  # 🔍 تتبع التحديثات
#
#        response = redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#        response.set_cookie(cookie_key, new_participants, max_age=60*60*24)  # حفظ الكوكيز ليوم
#
#        messages.success(request, "تم الانضمام إلى الشراء الجماعي بنجاح!")
#
#        # عند اكتمال العدد، يتم الحفظ في قاعدة البيانات
#        if len(participants_list) >= product.max_participants:
#            for user_id in participants_list:
#                user = get_object_or_404(User, id=user_id)
#                group_purchase.participants.add(user)
#
#            product.quantity = max(0, product.quantity - product.max_participants)
#            product.save()
#            group_purchase.is_active = False
#            group_purchase.save()
#
#            print(f"✅ تمت إضافة المشاركين إلى قاعدة البيانات: {participants_list}")  # ✅ تأكيد الحفظ في DB
#            response.delete_cookie(cookie_key)  # حذف الكوكيز بعد الحفظ في قاعدة البيانات
#
#    else:
#        messages.error(request, "يجب عليك تسجيل الدخول للانضمام إلى الشراء الجماعي!", "alert-danger")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    return response


#test for all 
#def create_group_purchase(request, product_id):
#    """إنشاء غرفة شراء جماعي أو الانضمام إلى غرفة مفتوحة."""
#    product = get_object_or_404(Product, id=product_id)
#
#    # العثور على الغرف المفتوحة لهذا المنتج مع عدد المشاركين
#    open_group_purchases = GroupPurchase.objects.filter(
#        product=product,
#        is_active=True
#    ).annotate(participant_count=Count('participants'))  # إضافة عد المشاركين بشكل صحيح
#
#    if request.method == 'POST':
#        action = request.POST.get('action')  # تحديد الإجراء (الانضمام أو الإنشاء)
#
#        if action == 'join' and 'group_purchase_id' in request.POST:
#            group_purchase_id = request.POST['group_purchase_id']
#            group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#            
#            # إذا كانت الغرفة مفتوحة وغير مكتملة العدد، سيتم الانضمام إليها
#            if group_purchase.is_active and group_purchase.participants.count() < group_purchase.product.max_participants:
#                return redirect('orders:join_group_purchase', group_purchase_id=group_purchase.id)
#            else:
#                messages.error(request, "عذراً، لا يمكنك الانضمام إلى هذه الغرفة لأنها مكتملة أو مغلقة.")
#                return redirect('orders:create_group_purchase', product_id=product.id)
#        
#        elif action == 'create':
#            # إنشاء غرفة شراء جماعي جديدة إذا لم توجد غرف مفتوحة
#            group_purchase = GroupPurchase.objects.create(product=product)
#            messages.success(request, "Group buying room created successfully!", "alert-success")
#            
#            # إنشاء الرابط الخاص للغرفة
#            group_purchase_link = request.build_absolute_uri(
#                reverse('orders:group_purchase_detail', args=[group_purchase.id])
#            )
#            
#            return render(request, 'orders/group_purchase_detail.html', {
#                'group_purchase': group_purchase,
#                'group_purchase_link': group_purchase_link,
#            })
#
#    return render(request, 'orders/create_group_purchase.html', {
#        'product': product,
#        'open_group_purchases': open_group_purchases  # إرسال الغرف المفتوحة للمستخدم
#    })
#test def join_group_purchase(request, group_purchase_id):
#    """الانضمام إلى الشراء الجماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    product = group_purchase.product
#    
#    if not check_group_purchase_availability(group_purchase, product):
#        messages.error(request, "عذرًا، هذا المنتج غير متوفر حاليًا أو تم الوصول للحد الأقصى من المشاركين!","alert-danger")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    if request.user.is_authenticated:
#        if request.user not in group_purchase.participants.all():
#            # إضافة المستخدم إلى قائمة المشاركين
#            group_purchase.participants.add(request.user)
#            product.quantity -= 1
#            product.save()
#            group_purchase.save()  # تأكد من حفظ الغرفة بعد إضافة المشارك
#
#            messages.success(request, "تم الانضمام إلى الشراء الجماعي بنجاح!", "alert-success")
#
#            # تحقق إذا تم الوصول للحد الأقصى من المشاركين أو المنتج نفد من المخزون
#            if group_purchase.participants.count() >= product.max_participants or product.quantity <= 0:
#                group_purchase.is_active = False
#                group_purchase.save()
#        else:
#            messages.warning(request, "أنت بالفعل مشارك في هذا الشراء الجماعي!")
#    else:
#        messages.error(request, "يجب عليك تسجيل الدخول للانضمام إلى الشراء الجماعي!", "alert-danger")
#
#    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)


#from django.shortcuts import render, redirect, get_object_or_404, reverse
#from django.http import HttpRequest, HttpResponse,Http404 
#from .models import Order, GroupPurchase
#from .forms import OrderForm
#from products.models import Product
#from django.contrib import messages
## Create your views here.
#
#def create_order_view(request, product_id):
#    product = get_object_or_404(Product, id=product_id)
#
#    if request.method == 'POST':
#        form = OrderForm(request.POST)
#        if form.is_valid():
#            order = form.save(commit=False)
#            order.user = request.user
#            order.product = product
#            order.order_type = Order.OrderType.INDIVIDUAL  
#            order.participants = 1 
#            order.save()
#            messages.success(request, "Individual order created successfully!")
#            return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#        else:
#            messages.error(request, "An error occurred while creating the request.")
#            return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#
#
#    else:
#        form = OrderForm()
#
#    return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#
#
#
#def create_group_purchase(request, product_id):
#    """إنشاء غرفة شراء جماعي وإعادة التوجيه إلى تفاصيلها"""
#    product = get_object_or_404(Product, id=product_id)
#    if request.method == 'POST':
#        group_purchase = GroupPurchase.objects.create(product=product)
#        messages.success(request, "Group buying room created successfully!")
#
#        # إنشاء الرابط الخاص للغرفة
#        group_purchase_link = request.build_absolute_uri(
#            reverse('orders:group_purchase_detail', args=[group_purchase.id])
#        )
#
#        # إضافة الرابط إلى الرسالة أو صفحة التفاصيل
#        return render(request, 'orders/group_purchase_detail.html', {
#            'group_purchase': group_purchase,
#            'group_purchase_link': group_purchase_link,
#        })
#
#    return render(request, 'orders/create_group_purchase.html', {'product': product})
#
#def group_purchase_detail(request, group_purchase_id):
#    """عرض تفاصيل غرفة الشراء الجماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    return render(request, 'orders/group_purchase_detail.html', {'group_purchase': group_purchase})
#
#
#def join_group_purchase(request, group_purchase_id):
#    """الانضمام إلى الشراء الجماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    product = group_purchase.product
#    max_participants = product.max_participants  # الحد الأقصى من المشاركين
#    
#    # التحقق من توافر المنتج أو الحد الأقصى للمشاركين
#    if product.quantity <= 0 or group_purchase.participants.count() >= max_participants:
#        group_purchase.is_active = False
#        group_purchase.save()
#        messages.error(request, "عذرًا، هذا المنتج غير متوفر حاليًا أو تم الوصول للحد الأقصى من المشاركين!")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#    
#    # السماح بالانضمام إذا لم يصل الحد
#    if request.user.is_authenticated:
#        if request.user not in group_purchase.participants.all():
#            group_purchase.add_participant(request.user)
#            product.quantity -= 1
#            product.save()
#            messages.success(request, "تم الانضمام إلى الشراء الجماعي بنجاح!")
#            
#            # غلق الغرفة إذا تم الوصول للحد الأقصى للمشاركين أو نفذت الكمية
#            if group_purchase.participants.count() >= max_participants or product.quantity <= 0:
#                group_purchase.is_active = False
#                group_purchase.save()
#        else:
#            messages.warning(request, "أنت بالفعل مشارك في هذا الشراء الجماعي!")
#    else:
#        messages.error(request, "يجب عليك تسجيل الدخول للانضمام إلى الشراء الجماعي!")
#
#    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#def create_order_in_group(request, group_purchase_id):
#    """إنشاء طلب داخل غرفة شراء جماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#
#    # التحقق من أن الشراء الجماعي ما زال مفتوحًا
#    if not group_purchase.is_active:
#        messages.error(request, "هذا الشراء الجماعي مغلق!")
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
#    if request.method == 'POST':
#        quantity = int(request.POST.get('quantity', 1))
#        
#        # تحديد السعر وفقًا للسعر الجماعي أو العادي
#        price = group_purchase.product.group_price if group_purchase.product.group_price else group_purchase.product.price
#        total_price = quantity * price
#
#        order = Order.objects.create(
#            user=request.user,
#            product=group_purchase.product,
#            quantity=quantity,
#            total_price=total_price,
#            order_type=Order.OrderType.GROUP,
#            group_purchase=group_purchase
#        )
#
#        # تحديث المشاركين بعد إضافة الطلب
#        group_purchase.add_participant(request.user)
#
#        messages.success(request, "تم إنشاء طلبك في الشراء الجماعي بنجاح!")
#        return redirect('orders:order_detail', order_id=order.id)
#
#    return render(request, 'orders/create_order_in_group.html', {'group_purchase': group_purchase})
#
#def order_detail(request, order_id):
#    """عرض تفاصيل الطلب"""
#    order = get_object_or_404(Order, id=order_id)
#    return render(request, 'orders/order_detail.html', {'order': order})
#
#
#








#def create_order_view(request, product_id):
#    product = Product.objects.get(id=product_id)
#    if request.method == 'POST':
#        form = OrderForm(request.POST)
#        if form.is_valid():
#            order = form.save(commit=False)
#            order.user = request.user
#            order.product = product
#            order.save()
#            #return redirect('order_success')  # أو أي صفحة أخرى
#    else:
#        form = OrderForm()
#    return render(request, 'orders/create_order.html', {'form': form, 'product': product})
#
#
#def create_group_purchase(request, product_id: int):
#    """إنشاء غرفة شراء جماعي"""
#    product = get_object_or_404(Product, id=product_id)
#    if request.method == 'POST':
#        group_purchase = GroupPurchase.objects.create(
#            product=product,
#        )
#        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#    return render(request, 'orders/create_group_purchase.html', {'product': product})
#
#def group_purchase_detail(request, group_purchase_id):
#    """عرض تفاصيل غرفة الشراء الجماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    product = group_purchase.product
#    return render(request, 'orders/group_purchase_detail.html', {'group_purchase': group_purchase, 'product': product})
#
#def join_group_purchase(request, group_purchase_id):
#    """الانضمام إلى غرفة شراء جماعي"""
#    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#    group_purchase.add_participant(request.user)
#    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
#
##22def create_order_in_group(request, group_purchase_id):
##    """إنشاء طلب داخل غرفة شراء جماعي"""
##    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
##    if request.method == 'POST':
##        quantity = int(request.POST.get('quantity'))
##        order = Order.objects.create(
##            user=request.user,
##            product=group_purchase.product,
##            quantity=quantity,
##            order_type=Order.OrderType.GROUP,
##            group_purchase=group_purchase
##        )
##        # إعادة تعيين عدد المشاركين والسعر إلى القيم الأصلية
##        #group_purchase.participants = 0
##        #group_purchase.total_price = group_purchase.product.group_price if group_purchase.product.group_price else 0
##        #group_purchase.save()
##        print(f"Participants after: {group_purchase.participants}")  # طباعة قيمة المشاركين بعد التغيير
##        updated_group_purchase = GroupPurchase.objects.get(id=group_purchase_id)
##        print(f"Participants after get: {updated_group_purchase.participants}") # طباعة قيمة المشاركين بعد الحصول عليها من قاعدة البيانات
##
##        return redirect('orders:order_detail', order_id=order.id)
##
##    return render(request, 'orders/create_order_in_group.html', {'group_purchase': group_purchase})
#
#def create_order_in_group(request, group_purchase_id):
#    if request.methode == 'POST':
#        group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
#        order = Order.objects.create(
#            user=request.user,
#            product=group_purchase.product,
#            quantity=int(request.POST.get('quantity')),
#            order_type=Order.OrderType.GROUP,
#            group_purchase=group_purchase
#        )
#        order.save()
#        return redirect('orders:order_detail', order_id=order.id)
#    return render(request, 'orders/create_order_in_group.html', {'group_purchase': group_purchase})
##def create_order_in_group(request, group_purchase_id):
##    """إنشاء طلب داخل غرفة شراء جماعي"""
##    group_purchase = get_object_or_404(GroupPurchase, id=group_purchase_id)
##    
##    if request.method == 'POST':
##        # بدلاً من الكمية، سنستخدم عدد المشاركين الحاليين في الشراء الجماعي
##        participants_count = group_purchase.participants  # عدد المشاركين الحاليين
##
##        # حساب السعر الإجمالي بناءً على عدد المشاركين
##        discount_price = group_purchase.product.group_price if group_purchase.product.group_price else group_purchase.product.price
##        total_price = discount_price * participants_count
##        
##        # إنشاء الطلب مع السعر الإجمالي بناءً على عدد المشاركين
##        order = Order.objects.create(
##            user=request.user,
##            product=group_purchase.product,
##            quantity=1,  # هنا يمكن تحديد الكمية كـ 1 لأننا نعمل بناءً على عدد المشاركين
##            total_price=total_price,  # السعر الكلي بناءً على الخصم وعدد المشاركين
##            order_type=Order.OrderType.GROUP,
##            group_purchase=group_purchase,  # ربط الطلب بالشراء الجماعي
##            participants=participants_count  # إضافة عدد المشاركين الحاليين
##        )
##        
##        # بعد إضافة الطلب، يمكن تحديث عدد المشاركين في الشراء الجماعي
##        group_purchase.add_participant(request.user)  # إضافة المستخدم إلى المشاركين
##        return redirect('orders:order_detail', order_id=order.id)
##
##    return render(request, 'orders/create_order_in_group.html', {'group_purchase': group_purchase})
##
#def order_detail(request, order_id):
#    """عرض تفاصيل الطلب"""
#    order = get_object_or_404(Order, id=order_id)
#    return render(request, 'orders/order_detail.html', {'order': order})
#
#
#