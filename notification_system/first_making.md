# 创建公告通知管理系统项目


以下是手动创建和初始化公告通知管理系统项目的详细步骤：

### 手动创建公告通知管理系统项目步骤

本指南将帮助您从零开始设置 Django 公告通知管理系统。

#### 1. 创建项目目录

首先，在您希望存放项目的任意位置创建一个新的文件夹。例如：

```bash
mkdir notification_system_project

cd notification_system_project
``

#### 2. 创建并激活虚拟环境

强烈建议为您的项目使用虚拟环境，以隔离项目依赖。

```bash
python3 -m venv venv
```
**激活虚拟环境：**

* **macOS / Linux:**

  ```bash
  source venv/bin/activate

  ```

* **Windows (Command Prompt):**

  ```cmd

  ./venv/Scripts/activate

  ```

* **Windows (PowerShell):**

  ```powershell

  ./venv/Scripts/Activate.ps1

  ```

  激活后，您的命令行提示符通常会显示 `(venv)` 字样。

#### 3. 安装 Django 和其他依赖

在**激活的虚拟环境**中，安装项目所需的库：

```bash
pip install Django djangorestframework markdown
```

#### 4. 创建 Django 项目

在 `notification_system_project` 目录下（与您刚刚创建的 `venv` 文件夹同级），创建 Django 项目：

```bash
django-admin startproject notification_system .

```

注意：末尾的 `.` 表示在当前目录下创建项目文件，而不是再创建一个嵌套的 `notification_system` 文件夹。

#### 5. 创建 Django 应用

在 `notification_system_project` 目录下，创建 `announcements` 应用：

```bash
python manage.py startapp announcements
```

#### 6. 配置 `settings.py`

打开 `notification_system/settings.py` 文件，进行以下修改：

* **导入 `Path` 模块并修改 `BASE_DIR`：**

  ```python

  from pathlib import Path

  BASE_DIR = Path(__file__).resolve().parent.parent

  ```

* **添加应用到 `INSTALLED_APPS`：**

  ```python

  INSTALLED_APPS = \[

      # ... 其他默认应用

      'announcements',

      'rest_framework',

  ]

  ```

* **设置语言和时区：**

  ```python

  LANGUAGE_CODE = 'zh-hans'

  TIME_ZONE = 'Asia/Shanghai'

  USE_I18N = True

  USE_L10N = True

  USE_TZ = True

  ```

* **配置全局模板目录 (可选，但推荐)：**

  ```python

  import os # 确保 os 已导入

  TEMPLATES = \[

      {

          'BACKEND': 'django.template.backends.django.DjangoTemplates',

          'DIRS': \[os.path.join(BASE_DIR, 'templates')], # 添加全局模板目录

          'APP_DIRS': True,

          'OPTIONS': {

              'context_processors': \[

                  'django.template.context_processors.debug',

                  'django.template.context_processors.request',

                  'django.contrib.auth.context_processors.auth',

                  'django.contrib.messages.context_processors.messages',

              ],

          },

      },

  ]

  ```

* **配置全局静态文件目录 (可选，但推荐)：**

  ```python

  STATIC_URL = '/static/'

  STATICFILES_DIRS = \[

      os.path.join(BASE_DIR, 'static'), # 添加全局静态文件目录

  ]

  ```

#### 7. 配置 `urls.py`

打开 `notification_system/urls.py` 文件，包含 `announcements` 应用的 URL：

```python

from django.contrib import admin

from django.urls import path, include

urlpatterns = \[

    path('admin/', admin.site.urls),

    path('announcements/', include('announcements.urls')),

    path('api/', include('announcements.api.urls')),

]
```

#### 8. 创建 `static` 目录

在项目根目录（与 `manage.py` 同级）创建 `static` 文件夹，用于存放全局静态文件：

```bash
mkdir static
```

#### 9. 创建 `announcements` 应用的文件

按照之前提供的代码，在 `announcements` 目录下创建以下文件和目录，并填充相应内容：

* `announcements/models.py`

* `announcements/forms.py`

* `announcements/views.py`

* `announcements/urls.py`

* `announcements/admin.py`

* `announcements/management/commands/init_announcements.py` (确保 `management/commands` 目录结构正确)

* `announcements/api/__init__.py`

* `announcements/api/serializers.py`

* `announcements/api/views.py`

* `announcements/api/urls.py`

#### 10. 创建模板文件

在项目根目录创建 `templates` 文件夹，并在其中创建 `announcements` 目录，然后将所有 HTML 模板文件放入其中：

```bash
mkdir templates

mkdir templates/announcements
```

然后将 `base.html`, `announcement_list.html`, `announcement_detail.html`, `announcement_form.html`, `announcement_confirm_delete.html`, `login.html` 等文件放入 `templates/announcements/` 目录。

#### 11. 数据库迁移

在项目根目录，确保虚拟环境已激活，运行数据库迁移命令：

```bash
python manage.py makemigrations announcements

python manage.py migrate
```

当提示为 `emergency_level_numeric` 字段提供默认值时，输入 `1`。

#### 12. 初始化数据

运行自定义管理命令来初始化超级管理员、用户组和公告分类：

```bash
python manage.py init_announcements
```

此命令会创建 `admin` 用户（密码 `123456`），`公告发布者` 和 `超级管理员` 用户组，并添加默认公告分类。

#### 13. 运行开发服务器

最后，在项目根目录，确保虚拟环境已激活，运行开发服务器：

```bash
python manage.py runserver
```

现在，您可以在浏览器中访问 `http://127.0.0.1:8000/announcements/` 来查看公告列表。通过 `http://127.0.0.1:8000/admin/` 访问 Django 管理后台，使用 `admin` 用户登录进行管理。
