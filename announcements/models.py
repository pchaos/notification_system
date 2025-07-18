# -*- coding=utf-8 -*-

# announcements/models.py

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import markdown

class Category(models.Model):
    """
    公告分类模型
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="分类描述")

    class Meta:
        verbose_name = "公告分类"
        verbose_name_plural = "公告分类"
        ordering = ['name']

    def __str__(self):
        return self.name

class Announcement(models.Model):
    """
    公告模型
    """
    EMERGENCY_LEVEL_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]

    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容 (支持Markdown)")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="分类")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发布者")
    publish_at = models.DateTimeField(default=timezone.now, verbose_name="计划发布时间")
    target_users = models.ManyToManyField(User, related_name='received_announcements', blank=True, verbose_name="指定接收用户")
    target_groups = models.ManyToManyField(Group, related_name='received_announcements_by_group', blank=True, verbose_name="指定接收用户组")
    emergency_level = models.CharField(max_length=10, choices=EMERGENCY_LEVEL_CHOICES, default='low', verbose_name="紧急程度")
    
    # 新增字段：用于数据库排序的紧急程度数值
    emergency_level_numeric = models.IntegerField(default=1, verbose_name="紧急程度数值") 

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"
        # 优先排序：根据新的 numeric 字段进行倒序排序，然后是发布时间倒序
        ordering = ['-emergency_level_numeric', '-publish_at']

    @property
    def is_published(self):
        """
        判断公告是否已发布（到达计划发布时间）
        """
        return self.publish_at <= timezone.now()

    def _get_emergency_level_numeric_value(self):
        """
        内部方法：根据 emergency_level 返回对应的数值
        """
        level_map = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        return level_map.get(self.emergency_level, 1) # 默认值为1 (low)

    def save(self, *args, **kwargs):
        """
        保存公告时自动设置 emergency_level_numeric 字段
        """
        self.emergency_level_numeric = self._get_emergency_level_numeric_value()
        super().save(*args, **kwargs)

    def get_markdown_content(self):
        """
        将Markdown内容渲染为HTML
        """
        return markdown.markdown(self.content, extensions=['extra', 'codehilite'])

    def __str__(self):
        return self.title

class ReadStatus(models.Model):
    """
    用户阅读状态模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, verbose_name="公告")
    read_at = models.DateTimeField(auto_now_add=True, verbose_name="阅读时间")

    class Meta:
        verbose_name = "阅读状态"
        verbose_name_plural = "阅读状态"
        unique_together = ('user', 'announcement') # 确保每个用户对每个公告只有一条阅读记录
        ordering = ['-read_at']

    def __str__(self):
        return f"{self.user.username} - {self.announcement.title} (已读)"
