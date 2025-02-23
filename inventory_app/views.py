import csv
import datetime
from time import timezone

from django.core.paginator import Paginator

from .models import User, Profile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum,F
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from . import models
from .forms import CustomUserCreationForm
from .models import Product, Supplier, Category, Sale, Profile
from django.db import models
from django.contrib import messages
from .models import PurchaseApplication

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, '注册成功！')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'注册失败：{str(e)}')
        else:
            # 获取表单错误信息并提示
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 检查用户是否有 Profile，如果没有则创建
            profile, created = Profile.objects.get_or_create(user=user)
            return redirect('product_management')
        else:
            # 添加调试信息
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"用户 {username} 认证失败")
            messages.error(request, '用户名或密码错误')
    return render(request, 'login.html')





def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def inventory_list(request):
    # 重定向到 product_management 页面
    return redirect('product_management')



@login_required
def edit_supplier(request):
    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        # 这里可以添加保存供应商信息的逻辑
        # 例如：创建新供应商或更新已有供应商信息
        Supplier.objects.create(name=supplier_name, phone=phone, email=email, address=address)
        # 继续保持在当前页面
        suppliers = Supplier.objects.all()
        return render(request, 'edit_supplier.html', {'suppliers': suppliers})
    else:
        suppliers = Supplier.objects.all()
        return render(request, 'edit_supplier.html', {'suppliers': suppliers})

@login_required
def product_management(request):
    # 获取搜索关键字
    query = request.GET.get('q')
    if query:
        # 根据关键字过滤商品列表
        products = Product.objects.filter(name__icontains=query) | Product.objects.filter(product_id__icontains=query)
    else:
        products = Product.objects.all()

    # 每页显示20个商品
    paginator = Paginator(products, 10)

    # 获取当前页码，默认为第1页
    page_number = request.GET.get('page', 1)

    # 获取当前页的商品数据
    page_obj = paginator.get_page(page_number)

    suppliers = Supplier.objects.all()  # 获取所有供应商

    context = {
        'products': page_obj,  # 将分页后的商品数据传递给模板
        'suppliers': suppliers
    }

    return render(request, 'product_management.html', context)
@login_required
def sales_management(request):
    # 获取搜索关键字
    query = request.GET.get('q')
    if query:
        # 根据关键字过滤销售记录列表
        sales = Sale.objects.filter(product__name__icontains=query) | Sale.objects.filter(product__product_id__icontains=query)
    else:
        sales = Sale.objects.all().order_by('-sale_time')

    # 创建 Paginator 对象，每页显示20条记录
    paginator = Paginator(sales, 12)

    # 获取当前页码
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'q': query,
    }
    return render(request, 'sales_management.html', context)

@login_required
def purchase_management(request):
    # 获取搜索关键字
    query = request.GET.get('q')

    if request.user.is_superuser:
        # 管理员可以查看所有采购申请记录
        if query:
            # 根据关键字过滤采购申请记录列表（假设PurchaseApplication模型中有product字段关联商品）
            applications = PurchaseApplication.objects.filter(product__name__icontains=query)
        else:
            # 获取所有采购申请记录
            applications = PurchaseApplication.objects.all()
    else:
        # 普通用户只能查看自己提交的采购申请记录
        if query:
            applications = PurchaseApplication.objects.filter(user=request.user, product__name__icontains=query)
        else:
            applications = PurchaseApplication.objects.filter(user=request.user)

    # 创建 Paginator 对象，每页显示20条记录
    paginator = Paginator(applications, 12)

    # 获取当前页码
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase_management.html', {'applications': page_obj, 'q': query})

@login_required
def query_statistics(request):
    # 获取当前日期
    today = timezone.now().date()

    # 计算当日销售额
    today_sales = Sale.objects.filter(sale_time__date=today).aggregate(total_sales=Sum(F('quantity') * F('product__price')))
    today_sales_amount = today_sales['total_sales'] if today_sales['total_sales'] else 0

    # 计算当日成本
    today_cost = Sale.objects.filter(sale_time__date=today).aggregate(total_cost=Sum(F('quantity') * F('product__purchase_price')))
    today_cost_amount = today_cost['total_cost'] if today_cost['total_cost'] else 0

    # 计算当日纯利润
    today_profit = today_sales_amount - today_cost_amount

    # 计算平台总销售额
    total_sales = Sale.objects.aggregate(total_sales=Sum(F('quantity') * F('product__price')))
    total_sales_amount = total_sales['total_sales'] if total_sales['total_sales'] else 0

    # 计算平台总成本
    total_cost = Sale.objects.aggregate(total_cost=Sum(F('quantity') * F('product__purchase_price')))
    total_cost_amount = total_cost['total_cost'] if total_cost['total_cost'] else 0

    # 计算平台总利润
    total_profit = total_sales_amount - total_cost_amount

    # 格式化金额到小数点后3位
    today_sales_amount = f"{today_sales_amount:.3f}"
    today_profit = f"{today_profit:.3f}"
    total_sales_amount = f"{total_sales_amount:.3f}"
    total_profit = f"{total_profit:.3f}"

    # 获取库存数量为 5 以下的商品列表
    low_stock_products = Product.objects.filter(quantity__lt=5)

    # 计算所有库存商品总值
    products = Product.objects.all()
    total_inventory_value = sum(product.purchase_price * product.quantity for product in products)

    context = {
        'today_sales': today_sales_amount,
        'today_profit': today_profit,
        'total_sales': total_sales_amount,
        'total_profit': total_profit,
        'low_stock_products': low_stock_products,
        'total_inventory_value': total_inventory_value,  # 传递所有库存商品总值到模板
    }

    return render(request, 'query_statistics.html', context)

@login_required
def export_all_products(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_products.csv"'

    writer = csv.writer(response)
    writer.writerow(['商品编号', '商品名称', '商品类别', '商品规格', '商品进价', '商品售价', '商品数量'])

    products = Product.objects.all()
    for product in products:
        writer.writerow([product.product_id, product.name, product.category, product.specification, product.purchase_price, product.price, product.quantity])

    return response

@login_required
def export_today_sales(request):
    today = timezone.now().date()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="today_sales.csv"'

    writer = csv.writer(response)
    writer.writerow(['商品编号', '商品名称', '商品类别', '商品规格', '商品售价', '销售数量', '销售时间'])

    sales = Sale.objects.filter(sale_time__date=today)
    for sale in sales:
        writer.writerow([sale.product.product_id, sale.product.name, sale.product.category, sale.product.specification, sale.product.price, sale.quantity, sale.sale_time])

    return response

@login_required
def export_total_sales(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="total_sales.csv"'

    writer = csv.writer(response)
    writer.writerow(['商品编号', '商品名称', '商品类别', '商品规格', '商品售价', '销售数量', '销售时间'])

    sales = Sale.objects.all()
    for sale in sales:
        writer.writerow([sale.product.product_id, sale.product.name, sale.product.category, sale.product.specification, sale.product.price, sale.quantity, sale.sale_time])

    return response


@login_required
def add_product(request):
    suppliers = Supplier.objects.all()
    categories = Category.objects.all()  # 获取所有商品类别
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        category_id = request.POST.get('category')  # 获取选择的商品类别ID
        category = Category.objects.get(id=category_id)  # 根据ID获取商品类别对象
        specification = request.POST.get('specification')
        purchase_price = request.POST.get('purchase_price')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        supplier_id = request.POST.get('supplier')
        supplier = Supplier.objects.get(id=supplier_id)
        Product.objects.create(
            product_id=product_id,
            name=name,
            category=category.name,  # 使用商品类别名称
            specification=specification,
            purchase_price=purchase_price,
            price=price,
            quantity=quantity,
            supplier=supplier
        )
        return redirect('product_management')
    return render(request, 'add_product.html', {'suppliers': suppliers, 'categories': categories})  # 传递商品类别信息给模板

@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        # 保存新的商品类别信息
        Category.objects.create(name=category_name)
        return redirect('add_category')  # 重定向到当前页面，避免重复提交

    # 获取已有类别信息
    categories = Category.objects.all()
    return render(request, 'add_category.html', {'categories': categories})




@login_required
def sell_product(request):
    # 获取搜索关键字
    query = request.GET.get('q')
    if query:
        # 根据关键字过滤商品列表
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)
        if product.quantity >= quantity:
            product.quantity -= quantity
            product.save()
            # 记录销售记录
            Sale.objects.create(product=product, quantity=quantity, sale_time=datetime.datetime.now())
            return redirect('sales_management')
        else:
            return HttpResponse("库存不足")

    return render(request, 'sell_product.html', {'products': products})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    suppliers = Supplier.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        product.product_id = request.POST.get('product_id')
        product.name = request.POST.get('name')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)
        product.category = category.name
        product.specification = request.POST.get('specification')
        product.purchase_price = request.POST.get('purchase_price')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        supplier_id = request.POST.get('supplier')
        supplier = Supplier.objects.get(id=supplier_id)
        product.supplier = supplier
        product.save()
        return redirect('product_management')

    return render(request, 'edit_product.html', {'product': product, 'suppliers': suppliers, 'categories': categories})



# 采购申请视图
@login_required
def purchase_application(request):
    # 获取搜索关键字
    query = request.GET.get('q')
    if query:
        # 根据关键字过滤商品列表
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)
        # 获取当前登录用户
        user = request.user
        # 创建 PurchaseApplication 对象时指定 user 字段的值
        PurchaseApplication.objects.create(user=user, product=product, quantity=quantity)
        return redirect('purchase_management')

    return render(request, 'purchase_application.html', {'products': products})
# 采购审批视图
@login_required
@user_passes_test(lambda u: u.is_superuser)
def purchase_approval(request):
    applications = PurchaseApplication.objects.filter(approved=False)
    return render(request, 'purchase_approval.html', {'applications': applications})

# 审批通过视图
@login_required
def approve_purchase(request, application_id):
    application = PurchaseApplication.objects.get(id=application_id)
    product = application.product
    product.quantity += application.quantity
    product.save()
    application.approved = True
    application.save()
    return redirect('purchase_approval')

@login_required
def edit_single_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        supplier.name = request.POST.get('supplier_name')
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        return redirect('edit_supplier')

    return render(request, 'edit_single_supplier.html', {'supplier': supplier})


@login_required
def export_suppliers(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'

    writer = csv.writer(response)
    writer.writerow(['供应商名称', '电话', '邮箱', '地址'])

    suppliers = Supplier.objects.all()
    for supplier in suppliers:
        writer.writerow([supplier.name, supplier.phone, supplier.email, supplier.address])

    return response

# 检查用户是否是管理员
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def user_management(request):
    # 获取所有用户及其对应的 Profile 信息
    users = User.objects.all()
    user_info_list = []
    for user in users:
        try:
            profile = user.profile
            user_info = {
                'user': user,
                'email': user.email,
                'phone_number': profile.phone_number
            }
        except Profile.DoesNotExist:
            # 如果用户没有 Profile，只显示用户的基本信息
            user_info = {
                'user': user,
                'email': user.email,
                'phone_number': None
            }
        user_info_list.append(user_info)
    # 打印 user_info_list 进行调试，查看是否正确获取用户信息
    print(user_info_list)
    return render(request, 'user_management.html', {'user_info_list': user_info_list})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
    except User.DoesNotExist:
        pass
    return redirect('user_management')


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # 处理表单提交
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        user.username = username
        user.email = email

        # 检查用户是否有 profile，如果没有则创建一个
        if not hasattr(user, 'profile'):
            from .models import Profile  # 假设 Profile 模型在当前 app 的 models.py 中
            profile = Profile(user=user)
            profile.save()

        user.profile.phone_number = phone_number
        user.save()
        user.profile.save()
        return redirect('user_management')
    return render(request, 'edit_user.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['用户名', '邮箱', '手机号'])

    users = User.objects.all()
    for user in users:
        writer.writerow([user.username, user.email, user.profile.phone_number])

    return response





