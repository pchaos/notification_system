#  公告通知管理系统

这是一个基于 Django 构建的公告通知管理系统，旨在提供一个多功能、响应式、支持多设备（PC、手机）的公告发布和管理平台。系统支持 Markdown 格式内容、按用户/用户组发布、定时发布、阅读状态跟踪、权限管理、紧急程度调整、分类管理、搜索以及微信小程序集成等功能。

## 功能特性

1.  **多设备支持**: 采用响应式设计，适配 PC、手机（苹果、安卓）等多种设备显示。

2.  **Markdown 内容**: 公告内容支持 Markdown 格式，提供丰富的文本编辑能力。

3.  **按用户/用户组发布**: 公告可以发布给指定的用户或特定的用户组，实现精准推送。

4.  **定时发布**: 可设置公告的计划发布时间，未到指定时间前，用户无法看到公告内容。

5.  **消息推送**: (此功能需要额外集成第三方推送服务, 如 FCM 或微信模板消息, 本系统提供接口扩展点。)

6.  **阅读状态跟踪**: 用户查看公告详细内容后, 系统会自动将该公告标记为“已读”。

7.  **分页设置与保存**: 用户可以自定义每页显示的公告数量, 系统会自动保存用户的设置偏好。

8.  **发布权限管理**: 只有属于“公告发布者”用户组的用户或超级管理员才能发布、编辑和删除公告。

9.  **紧急程度调整**: 公告可设置紧急程度（低、中、高、紧急）, 不同紧急程度的公告标题在列表和详情页会显示不同颜色, 并在列表页优先排序。

10. **接收公告/通知**: 用户能够接收到对其可见的系统推送的公告/通知, 并可以查看详细内容。

11. **公告/通知分类管理**: 对公告/通知进行分类管理, 方便用户查找和组织。

12. **公告/通知查看**: 用户可以查看公告/通知的详细内容。

13. **公告/通知搜索**: 用户可以通过关键词（标题或内容）搜索已发布的公告/通知。

14. **公告/通知阅读状态跟踪**: 系统记录用户是否已阅读某条公告/通知, 方便统计和管理。

15. **消息类型多样化**: 支持文本、图片、链接等多种消息类型（目前主要为文本, 但已提供字段扩展点）。

16. **权限管理**: 根据用户角色和权限, 限制不同用户对公告/通知的发布、查看和管理权限。

17. **历史记录**: 系统保存所有历史公告/通知, 方便用户查阅和追溯。

18. **微信小程序支持**: 提供 RESTful API 接口, 支持微信小程序作为前端应用。

19. **可集成性**: 可作为 Django 应用轻松集成到其他 Django 项目中。

## 技术栈

* **后端**: Django 5.x, Django REST Framework

* **数据库**: SQLite (开发默认), 可配置为 PostgreSQL, MySQL 等

* **前端**: Django 模板系统, HTML5, Tailwind CSS (响应式设计), JavaScript

* **内容渲染**: Markdown (Python `markdown` 库)

## 快速开始

### 1. 克隆仓库 (如果您从Git获取)

```bash
# git clone <您的仓库地址>

# cd notification_system

```

### 2. 创建并激活虚拟环境

推荐使用虚拟环境来管理项目依赖。

```bash
python -m venv venv

# Windows

./venv/Scripts/activate

# macOS/Linux

source venv/bin/activate

```

### 3. 安装依赖

```bash
pip install -r requirements.txt

# 或者手动安装:

# pip install django djangorestframework markdown
```

### 4. 数据库迁移

应用模型变更到数据库。

```bash
python manage.py makemigrations announcements

python manage.py migrate
```

### 5. 初始化数据

运行自定义管理命令来初始化超级管理员、用户组和公告分类。

```bash
python manage.py init_announcements
```

**注意**:

* 此命令会创建一个超级管理员用户：`admin`, 密码：`123456`。

* 同时会创建 `公告发布者` 和 `超级管理员` 用户组, 并赋予相应的公告管理权限。

* 还会创建默认的公告分类：`公告`, `通知`, `新闻`, `活动`, `活动通知`, `紧急通知`。

### 6. 运行开发服务器

```bash
python manage.py runserver
```

现在, 您可以在浏览器中访问 `http://127.0.0.1:8000/announcements/` 来查看公告列表。

通过 `http://127.0.0.1:8000/admin/` 访问 Django 管理后台, 使用 `admin` 用户登录进行管理。

## 使用说明

### 访问前端页面

* **公告列表**: `http://127.00.1:8000/announcements/`

* **登录页面**: `http://127.00.1:8000/announcements/login/`

### 发布公告

1.  登录 Django 管理后台 (`/admin/`), 确保您的用户属于 `公告发布者` 组或为超级管理员。

2.  或者, 通过前端页面登录后, 如果您的用户有发布权限, 可以看到“发布公告”按钮。

3.  填写公告标题、内容（支持 Markdown）、选择分类、设置计划发布时间、选择紧急程度, 并可指定接收用户或用户组。

### 权限管理

* **超级管理员**: 拥有所有权限, 可以管理所有公告、用户和组。

* **公告发布者**: 拥有发布、编辑、删除和查看公告的权限。

* **普通用户**: 只能查看对其可见的公告, 并自动标记已读。

您可以在 Django 管理后台 (`/admin/auth/group/`) 中管理用户组和权限。

### 响应式设计

系统前端使用 Tailwind CSS 构建, 自动适应不同屏幕尺寸（PC、平板、手机）。

## 集成到其他 Django 项目

要将此公告系统集成到您的现有 Django 项目中, 请遵循以下步骤：

1.  **复制 `announcements` 应用**: 将 `announcements` 文件夹复制到您的 Django 项目的根目录或您存放应用的目录中。

2.  **修改 `settings.py`**:

    在您的项目 `settings.py` 的 `INSTALLED_APPS` 中添加 `'announcements'` 和 `'rest_framework'`。

```python

    INSTALLED_APPS = \[

        # ... 其他应用

        'announcements',

        'rest_framework',

    ]

```

    同时, 确保 `TIME_ZONE` 和 `LANGUAGE_CODE` 设置正确, 以支持定时发布和中文显示。

3.  **修改 `urls.py`**:

    在您的项目 `urls.py` 中添加 `announcements` 应用的 URL 配置。

```python

    from django.urls import path, include

    urlpatterns = \[

        # ... 其他 URL

        path('announcements/', include('announcements.urls')),

        path('api/', include('announcements.api.urls')), # 如果您需要API

    ]

```

4.  **运行数据库迁移**:

```bash
    python manage.py makemigrations announcements

    python manage.py migrate

```

5.  **初始化数据 (可选)**:

    如果您需要初始化默认的超级管理员、用户组和分类, 可以运行：

```bash
    python manage.py init_announcements

```

    **注意**: 如果您的项目已有超级管理员, 此命令不会重复创建, 但会创建用户组和分类。

6.  **静态文件**:

    确保您的 `settings.py` 中 `STATIC_URL` 和 `STATICFILES_DIRS` 配置正确, 以便正确加载 Tailwind CSS。

## 贡献

欢迎通过提交 Pull Request 或 Issue 来贡献代码和提出建议。

## 许可证

[待定, 例如 MIT 许可证]
