# -*- coding=utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from announcements.models import Announcement, Category, ReadStatus

class Command(BaseCommand):
    help = 'Initializes the announcement system with default users, groups, permissions, and categories.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('开始初始化公告系统数据...'))

        # 1. 创建超级管理员用户
        try:
            admin_user, created = User.objects.get_or_create(username='admin', defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            })
            if created:
                admin_user.set_password('123456')
                admin_user.save()
                self.stdout.write(self.style.SUCCESS('成功创建超级管理员用户: admin (密码: 123456)'))
            else:
                self.stdout.write(self.style.WARNING('超级管理员用户 admin 已存在。'))
        except Exception as e:
            raise CommandError(f'创建超级管理员失败: {e}')

        # 获取 Announcement 模型的 ContentType
        announcement_content_type = ContentType.objects.get_for_model(Announcement)

        # 定义公告发布者所需的权限
        # Django会自动为每个模型创建 add, change, delete, view 权限
        add_announcement_perm = Permission.objects.get(
            content_type=announcement_content_type, codename='add_announcement'
        )
        change_announcement_perm = Permission.objects.get(
            content_type=announcement_content_type, codename='change_announcement'
        )
        delete_announcement_perm = Permission.objects.get(
            content_type=announcement_content_type, codename='delete_announcement'
        )
        view_announcement_perm = Permission.objects.get(
            content_type=announcement_content_type, codename='view_announcement'
        )

        # 2. 创建用户组并赋予权限
        # 公告发布者组
        announcer_group, created = Group.objects.get_or_create(name='公告发布者')
        if created:
            announcer_group.permissions.add(
                add_announcement_perm,
                change_announcement_perm,
                delete_announcement_perm,
                view_announcement_perm
            )
            self.stdout.write(self.style.SUCCESS('成功创建用户组: 公告发布者 并赋予相关权限。'))
        else:
            self.stdout.write(self.style.WARNING('用户组 公告发布者 已存在。'))

        # 超级管理员组 (通常不需要单独创建，因为超级管理员用户默认拥有所有权限)
        # 但如果需要一个名为“超级管理员”的组，可以这样创建
        superuser_group, created = Group.objects.get_or_create(name='超级管理员')
        if created:
            # 超级管理员组可以拥有所有权限，这里只添加公告相关的
            superuser_group.permissions.add(
                add_announcement_perm,
                change_announcement_perm,
                delete_announcement_perm,
                view_announcement_perm
            )
            # 可以根据需要添加更多权限
            self.stdout.write(self.style.SUCCESS('成功创建用户组: 超级管理员 并赋予相关权限。'))
        else:
            self.stdout.write(self.style.WARNING('用户组 超级管理员 已存在。'))

        # 3. 自动添加公告分类
        categories = [
            '公告', '通知', '新闻', '活动', '活动通知', '紧急通知'
        ]
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'成功添加公告分类: {cat_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'公告分类 {cat_name} 已存在。'))

        self.stdout.write(self.style.SUCCESS('公告系统数据初始化完成。'))
