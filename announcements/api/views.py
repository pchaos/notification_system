# -*- coding=utf-8 -*-

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User, Group

from announcements.models import Announcement, Category, ReadStatus
from .serializers import AnnouncementSerializer, CategorySerializer, ReadStatusSerializer, UserSerializer, GroupSerializer
from announcements.views import ANNOUNCER_PERMISSIONS # 导入权限定义

class IsAnnouncerOrAdmin(DjangoModelPermissions):
    """
    自定义权限：检查用户是否是超级管理员或属于“公告发布者”组
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        # 超级管理员拥有所有权限
        if request.user and request.user.is_superuser:
            return True
        # 否则，使用DjangoModelPermissions进行检查
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # 超级管理员拥有所有权限
        if request.user and request.user.is_superuser:
            return True
        # 否则，使用DjangoModelPermissions进行检查
        return super().has_object_permission(request, view, obj)


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    公告API视图集：
    - 提供公告的CRUD操作
    - 列表支持过滤、搜索、分页
    - 详情自动标记已读
    - 权限控制
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, IsAnnouncerOrAdmin] # 默认需要认证和发布者/管理员权限

    def get_queryset(self):
        """
        根据用户权限和可见性过滤公告
        - GET 请求 (list, retrieve): 仅显示用户可见且已发布的公告
        - 其他请求 (create, update, delete): 权限由 IsAnnouncerOrAdmin 控制
        """
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            # 获取所有已发布的公告
            queryset = Announcement.objects.filter(publish_at__lte=timezone.now()).distinct()

            # 过滤用户可见的公告：
            # 1. 发布给所有用户 (target_users为空且target_groups为空)
            # 2. 发布给当前用户 (target_users包含当前用户)
            # 3. 发布给当前用户所属的用户组 (target_groups包含当前用户所属的任何组)
            queryset = queryset.filter(
                Q(target_users__isnull=True, target_groups__isnull=True) | # 发布给所有用户
                Q(target_users=user) | # 发布给当前用户
                Q(target_groups__in=user.groups.all()) # 发布给当前用户所属的组
            ).distinct()

            # 搜索功能
            query = self.request.query_params.get('q', None)
            if query:
                queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))

            # 排序：紧急程度优先，然后发布时间倒序
            return queryset.order_by('-emergency_level_order', '-publish_at')
        
        # 对于非 GET 请求，如果用户是超级管理员，显示所有公告
        # 否则，只显示用户自己发布的公告 (如果需要)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='公告发布者').exists():
            return Announcement.objects.all()
        return Announcement.objects.filter(author=self.request.user)


    def perform_create(self, serializer):
        """
        创建公告时，自动设置发布者为当前请求用户
        """
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        获取公告详情时，自动标记为已读
        """
        instance = self.get_object()
        if request.user.is_authenticated:
            ReadStatus.objects.get_or_create(user=request.user, announcement=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_announcements(self, request):
        """
        获取当前用户已读/未读的公告列表
        """
        user = request.user
        read_status_filter = request.query_params.get('read_status', None) # 'read' 或 'unread'

        # 获取用户可见的公告
        queryset = self.get_queryset() # 使用get_queryset来获取用户可见的公告

        if read_status_filter == 'read':
            read_announcement_ids = ReadStatus.objects.filter(user=user).values_list('announcement__id', flat=True)
            queryset = queryset.filter(id__in=read_announcement_ids)
        elif read_status_filter == 'unread':
            read_announcement_ids = ReadStatus.objects.filter(user=user).values_list('announcement__id', flat=True)
            queryset = queryset.exclude(id__in=read_announcement_ids)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    公告分类API视图集：
    - 提供分类的列表和详情（只读）
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated] # 认证用户即可查看

class ReadStatusViewSet(viewsets.ModelViewSet):
    """
    阅读状态API视图集：
    - 提供阅读状态的CRUD操作 (主要用于查看和创建/删除自己的阅读状态)
    """
    queryset = ReadStatus.objects.all()
    serializer_class = ReadStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        用户只能查看和管理自己的阅读状态
        """
        return ReadStatus.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        创建阅读状态时，自动设置用户为当前请求用户
        """
        # 确保不会重复创建
        announcement_id = self.request.data.get('announcement')
        if not announcement_id:
            raise serializers.ValidationError({"announcement": "公告ID是必填项。"})
        
        announcement = Announcement.objects.get(id=announcement_id)
        ReadStatus.objects.get_or_create(user=self.request.user, announcement=announcement)
        # 返回已存在的或新创建的实例
        serializer.instance = ReadStatus.objects.get(user=self.request.user, announcement=announcement)

    def destroy(self, request, *args, **kwargs):
        """
        删除阅读状态 (标记为未读)
        """
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 用户和用户组的只读视图集，方便前端获取选项
class UserReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # 仅管理员可见

class GroupReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # 仅管理员可见
