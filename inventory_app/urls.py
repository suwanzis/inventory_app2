from django.urls import path

from . import views
from .views import register, user_login, user_logout, home, product_management, sales_management, \
    purchase_management, query_statistics, add_product, add_category, sell_product, edit_supplier, edit_product, \
    purchase_application, purchase_approval, approve_purchase, edit_single_supplier, export_suppliers, user_management, \
    delete_user, export_users_csv, edit_user

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('product_management/', product_management, name='product_management'),
    path('sales_management/', sales_management, name='sales_management'),
    path('purchase_management/', purchase_management, name='purchase_management'),
    path('query_statistics/', query_statistics, name='query_statistics'),

    path('export_all_products/', views.export_all_products, name='export_all_products'),
    path('export_today_sales/', views.export_today_sales, name='export_today_sales'),
    path('export_total_sales/', views.export_total_sales, name='export_total_sales'),
    path('export_suppliers/', export_suppliers, name='export_suppliers'),

    path('add_product/', add_product, name='add_product'),
    path('add_category/', add_category, name='add_category'),
    path('sell_product/', sell_product, name='sell_product'),
    path('edit_supplier/', edit_supplier, name='edit_supplier'),
    path('edit_supplier/<int:supplier_id>/', edit_single_supplier, name='edit_single_supplier'),
    path('edit_product/<int:product_id>/', edit_product, name='edit_product'),  # 添加 edit_product 的 URL 配置

    path('purchase_application/', purchase_application, name='purchase_application'),
    path('purchase_approval/', purchase_approval, name='purchase_approval'),
    path('approve_purchase/<int:application_id>/', approve_purchase, name='approve_purchase'),

    path('user_management/', user_management, name='user_management'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),

    path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('export_users_csv/', export_users_csv, name='export_users_csv'),

]