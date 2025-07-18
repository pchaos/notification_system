# -*- coding=utf-8 -*-

from django.urls import path
from .views import (
    AnnouncementListView,
    AnnouncementDetailView,
    AnnouncementCreateView,
    AnnouncementUpdateView,
    AnnouncementDeleteView,
)
from django.contrib.auth import views as auth_views # 导入Django内置的认证视图

urlpatterns = [
    # 公告列表 (主页)
    path('', AnnouncementListView.as_view(), name='announcement_list'),
    # 公告详情
    path('<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    # 创建公告
    path('create/', AnnouncementCreateView.as_view(), name='announcement_create'),
    # 编辑公告
    path('<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='announcement_edit'),
    # 删除公告
    path('<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),

    # 登录和登出视图 (如果您没有自定义认证系统，可以使用Django内置的)
    path('login/', auth_views.LoginView.as_view(template_name='announcements/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='announcement_list'), name='logout'),
]
