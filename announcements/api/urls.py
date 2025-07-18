# -*- coding=utf-8 -*-

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnnouncementViewSet,
    CategoryViewSet,
    ReadStatusViewSet,
    UserReadOnlyViewSet,
    GroupReadOnlyViewSet,
)

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'read-status', ReadStatusViewSet)
router.register(r'users', UserReadOnlyViewSet)  # 提供用户列表，用于公告指定接收者
router.register(r'groups', GroupReadOnlyViewSet)  # 提供用户组列表，用于公告指定接收组

urlpatterns = [
    path('', include(router.urls)),
    # DRF 提供的认证URL，用于获取token等
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
