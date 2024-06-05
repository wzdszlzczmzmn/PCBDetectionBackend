## README

#### 1、conda虚拟环境构建

- 使用如下命令创建Python虚拟环境（<envName>为你所创建的虚拟环境的名称）

```shell
conda create --name <envName> python=3.8
```

- 使用如下命令启用虚拟环境

```shell
conda activate <envName>
```

- 安装项目环境

```shell
pip install -r requirements.txt
```

#### 2、数据库环境配置

- 打开PCBDetectionBackend/settings.py
- 在如下部分配置数据库相关信息

```
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "PCBDetection",
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

