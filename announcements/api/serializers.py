# -*- coding=utf-8 -*-

from rest_framework import serializers
from announcements.models import Announcement, Category, ReadStatus
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    """
    公告分类序列化器
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class UserSerializer(serializers.ModelSerializer):
    """
    用户基本信息序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username']

class GroupSerializer(serializers.ModelSerializer):
    """
    用户组序列化器
    """
    class Meta:
        model = Group
        fields = ['id', 'name']

class AnnouncementSerializer(serializers.ModelSerializer):
    """
    公告序列化器
    """
    category = CategorySerializer(read_only=True) # 只读，显示分类名称
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True
    ) # 用于创建/更新时通过ID选择分类

    author = UserSerializer(read_only=True) # 只读，显示发布者用户名
    target_users = UserSerializer(many=True, read_only=True) # 只读，显示指定用户列表
    target_users_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    ) # 用于创建/更新时通过ID选择指定用户

    target_groups = GroupSerializer(many=True, read_only=True) # 只读，显示指定用户组列表
    target_groups_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, write_only=True, required=False
    ) # 用于创建/更新时通过ID选择指定用户组

    is_read = serializers.SerializerMethodField() # 用于显示当前用户是否已读

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'category', 'category_id', 'author',
            'publish_at', 'is_published', 'target_users', 'target_users_ids',
            'target_groups', 'target_groups_ids', 'emergency_level',
            'created_at', 'updated_at', 'is_read'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'is_published']

    def get_is_read(self, obj):
        """
        判断当前请求用户是否已阅读该公告
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReadStatus.objects.filter(user=request.user, announcement=obj).exists()
        return False

    def create(self, validated_data):
        target_users_ids = validated_data.pop('target_users_ids', [])
        target_groups_ids = validated_data.pop('target_groups_ids', [])
        
        # 确保author在validated_data中，或者从request中获取
        if 'author' not in validated_data and self.context.get('request') and self.context['request'].user.is_authenticated:
            validated_data['author'] = self.context['request'].user

        announcement = Announcement.objects.create(**validated_data)
        announcement.target_users.set(target_users_ids)
        announcement.target_groups.set(target_groups_ids)
        return announcement

    def update(self, instance, validated_data):
        target_users_ids = validated_data.pop('target_users_ids', None)
        target_groups_ids = validated_data.pop('target_groups_ids', None)

        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.category = validated_data.get('category', instance.category)
        instance.publish_at = validated_data.get('publish_at', instance.publish_at)
        instance.emergency_level = validated_data.get('emergency_level', instance.emergency_level)
        instance.save()

        if target_users_ids is not None:
            instance.target_users.set(target_users_ids)
        if target_groups_ids is not None:
            instance.target_groups.set(target_groups_ids)
        
        return instance

class ReadStatusSerializer(serializers.ModelSerializer):
    """
    阅读状态序列化器
    """
    announcement = AnnouncementSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = ReadStatus
        fields = ['id', 'user', 'announcement', 'read_at']
        read_only_fields = ['user', 'read_at']
