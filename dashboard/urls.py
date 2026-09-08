from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "orders/",
        views.order_list,
        name="order_list"
    ),

    path(
        'orders/<int:pk>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
        "orders/<int:pk>/update-status/",
        views.update_order_status,
        name="update_order_status"
    ),

    path(
        "orders/<int:pk>/invoice/",
        views.order_invoice,
        name="order_invoice"
    ),

    path(
        "orders/<int:pk>/invoice/pdf/",
        views.download_invoice_pdf,
        name="download_invoice_pdf"
    ),

    path(
        "orders/export/",
        views.export_orders_excel,
        name="export_orders_excel"
    ),

    path(
        "orders/bulk-delete/",
        views.bulk_delete_orders,
        name="bulk_delete_orders"
    ),

    path(
        "orders/delete/<int:pk>/",
        views.order_delete,
        name="order_delete"
    ),

    path(
        "products/",
        views.product_list,
        name="product_list"
    ),

    path(
        "products/add/",
        views.product_create,
        name="product_create",
    ),

    path(
        "products/<int:pk>/edit/",
        views.product_update,
        name="product_update",
    ),

    path(
        "products/<int:pk>/delete/",
        views.delete_gallery_image,
        name="delete_gallery_image",
    ),

    path(
        "categories/",
        views.category_list,
        name="category_list"
    ),

    path(
        "categories/add/",
        views.category_create,
        name="category_create",
    ),

    path(
    "categories/<int:pk>/edit/",
    views.category_update,
    name="category_update",
),

path(
    "categories/delete/<int:pk>/",
    views.category_delete,
    name="category_delete",
),

path(
    "customers/",
    views.customer_list,
    name="customer_list"
),

path(
    "customers/<int:pk>/",
    views.customer_detail,
    name="customer_detail",
),

path("sellers/", views.seller_list, name="seller_list"),

path(
    "sellers/<int:pk>/",
    views.seller_detail,
    name="seller_detail"
),

path(
    "sellers/<int:pk>/toggle-status/",
    views.seller_toggle_status,
    name="seller_toggle_status",
),

path(
    "customers/<int:pk>/toggle-status/",
    views.customer_toggle_status,
    name="customer_toggle_status",
),

path(
    "coupons/",
    views.coupon_list,
    name="coupon_list"
),

path(
    "coupons/create/",
    views.create_coupon,
    name="create_coupon"
),

path(
    "coupons/<int:coupon_id>/edit/",
    views.edit_coupon,
    name="edit_coupon"
),

path(
    "coupons/<int:coupon_id>/",
    views.coupon_detail,
    name="coupon_detail"
),

path(
    "coupons/<int:coupon_id>/delete/",
    views.delete_coupon,
    name="delete_coupon"
),

path(
    "reports/",
    views.report,
    name="report"
),

path(
    "reports/pdf/",
    views.download_sales_report_pdf,
    name="download_sales_report_pdf"
),

path(
    "reports/excel/",
    views.download_sales_report_excel,
    name="download_sales_report_excel"
),

path("reviews/", views.review_list, name="review_list"),
]