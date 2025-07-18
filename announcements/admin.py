# -*- coding=utf-8 -*-

from django.contrib import admin

from .models import Announcement, Category, ReadStatus


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    公告分类管理界面
    """

    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    公告管理界面
    """

    list_display = (
        'title',
        'category',
        'author',
        'publish_at',
        'is_published',
        'emergency_level',
        'created_at',
        'updated_at',
    )
    list_filter = ('category', 'author', 'emergency_level', 'publish_at')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)  # 对于ForeignKey字段，如果数据量大，使用raw_id_fields可以提高性能
    date_hierarchy = 'publish_at'  # 按日期分层导航
    fieldsets = (
        (None, {'fields': ('title', 'content', 'category', 'emergency_level')}),
        (
            '发布设置',
            {
                'fields': ('publish_at', 'target_users', 'target_groups'),
                'description': '设置公告的发布时间、指定接收用户和用户组。',
            },
        ),
        (
            '时间信息',
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),  # 折叠该部分
            },
        ),
    )
    readonly_fields = ('created_at', 'updated_at')  # 这些字段只读

    def get_queryset(self, request):
        # 在管理界面中，超级用户可以看到所有公告，普通用户只能看到自己发布的公告
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        # 在保存公告时，如果作者未设置，则自动设置为当前用户
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(ReadStatus)
class ReadStatusAdmin(admin.ModelAdmin):
    """
    阅读状态管理界面
    """

    list_display = ('user', 'announcement', 'read_at')
    list_filter = ('user', 'announcement', 'read_at')
    search_fields = ('user__username', 'announcement__title')
    raw_id_fields = ('user', 'announcement')  # 对于ForeignKey字段，使用raw_id_fields
