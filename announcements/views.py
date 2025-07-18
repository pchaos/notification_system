# -*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User, Group

from .models import Announcement, ReadStatus, Category
from .forms import AnnouncementForm

# 定义公告发布者组的权限
# 这些权限会在管理命令中创建并分配给相应的组
ANNOUNCER_PERMISSIONS = (
    'announcements.add_announcement',
    'announcements.change_announcement',
    'announcements.delete_announcement',
    'announcements.view_announcement', # 查看公告的权限
)

class AnnouncementListView(LoginRequiredMixin, ListView):
    """
    公告列表视图：
    - 显示用户可见的公告
    - 支持搜索（标题、内容）
    - 支持分页，并保存用户偏好
    - 紧急程度优先排序
    - 标记已读/未读状态
    """
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 10 # 默认每页显示10条

    def get_queryset(self):
        user = self.request.user
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
        ).distinct() # 使用distinct防止重复

        # 搜索功能
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))

        # 根据用户偏好设置分页大小
        page_size = self.request.GET.get('page_size')
        if page_size and page_size.isdigit():
            self.paginate_by = int(page_size)
            self.request.session['announcement_page_size'] = self.paginate_by # 保存用户偏好到session
        elif 'announcement_page_size' in self.request.session:
            self.paginate_by = self.request.session['announcement_page_size']

        return queryset.order_by('-emergency_level_order', '-publish_at') # 按照紧急程度和发布时间排序

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # 获取当前用户已读的公告ID列表
        read_announcement_ids = ReadStatus.objects.filter(user=user).values_list('announcement__id', flat=True)

        # 为每条公告添加 'is_read' 属性
        for announcement in context['announcements']:
            announcement.is_read = announcement.id in read_announcement_ids

        context['current_page_size'] = self.paginate_by
        context['query'] = self.request.GET.get('q', '')
        context['page_sizes'] = [5, 10, 20, 50] # 可选的分页大小
        return context

class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    """
    公告详情视图：
    - 显示公告详细内容
    - 自动标记为“已读”
    """
    model = Announcement
    template_name = 'announcements/announcement_detail.html'
    context_object_name = 'announcement'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # 检查用户是否有权限查看此公告
        # 1. 发布给所有用户 (target_users为空且target_groups为空)
        # 2. 发布给当前用户 (target_users包含当前用户)
        # 3. 发布给当前用户所属的用户组 (target_groups包含当前用户所属的任何组)
        is_visible_to_user = (
            (obj.target_users.count() == 0 and obj.target_groups.count() == 0) or
            (user in obj.target_users.all()) or
            (user.groups.filter(id__in=obj.target_groups.all().values_list('id', flat=True)).exists())
        )

        if not is_visible_to_user:
            messages.error(self.request, "您无权查看此公告。")
            return redirect('announcement_list') # 或者抛出403错误

        # 标记为已读
        ReadStatus.objects.get_or_create(user=user, announcement=obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 渲染Markdown内容到HTML
        context['rendered_content'] = self.object.get_markdown_content()
        return context


class AnnouncementCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    公告创建视图：
    - 只有具有 'add_announcement' 权限的用户才能访问
    """
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/announcement_form.html'
    success_url = reverse_lazy('announcement_list')
    permission_required = ANNOUNCER_PERMISSIONS # 需要公告发布权限

    def form_valid(self, form):
        form.instance.author = self.request.user # 自动设置发布者为当前用户
        messages.success(self.request, "公告发布成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = '发布新公告'
        return context

class AnnouncementUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    公告编辑视图：
    - 只有具有 'change_announcement' 权限的用户才能访问
    - 只能编辑自己发布的公告（可选，目前是只要有权限就能编辑所有）
    """
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/announcement_form.html'
    success_url = reverse_lazy('announcement_list')
    permission_required = ANNOUNCER_PERMISSIONS # 需要公告编辑权限

    def get_queryset(self):
        # 只有具有编辑权限的用户才能看到所有公告
        # 如果需要限制只能编辑自己的公告，可以添加：
        # if not self.request.user.is_superuser:
        #     return super().get_queryset().filter(author=self.request.user)
        return super().get_queryset()

    def form_valid(self, form):
        messages.success(self.request, "公告更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = '编辑公告'
        return context

class AnnouncementDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    公告删除视图：
    - 只有具有 'delete_announcement' 权限的用户才能访问
    """
    model = Announcement
    template_name = 'announcements/announcement_confirm_delete.html'
    success_url = reverse_lazy('announcement_list')
    permission_required = ANNOUNCER_PERMISSIONS # 需要公告删除权限

    def form_valid(self, form):
        messages.success(self.request, "公告删除成功！")
        return super().form_valid(form)

    def get_queryset(self):
        # 只有具有删除权限的用户才能看到所有公告
        # 如果需要限制只能删除自己的公告，可以添加：
        # if not self.request.user.is_superuser:
        #     return super().get_queryset().filter(author=self.request.user)
        return super().get_queryset()
