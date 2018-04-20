#### 搭建一个短视频后台

ubuntu 16.0.4

#### 简介
> 基于ffmpeg 和mediainfo，ffmpeg将视频生成animated webp、 gif、 thum jpg，
 mediainfo獲取視頻的詳細信息，
 最終以json返回给客户端

#### 依赖
- ffmpeg
安装ffmpeg
```
sudo add-apt-repository ppa:kirillshkrogalev/ffmpeg-next
sudo apt-get update
sudo apt-get install ffmpeg
```
- mediainfo
安装mediainfo
```
sudo add-apt-repository ppa:shiki/mediainfo
sudo apt-get update
sudo apt-get install mediainfo mediainfo-gui
mediainfo-gui即可启动
```
- redis-server
安装redis-server
```
sudo apt-get install -y python-software-properties
sudo apt-get install software-properties-common
sudo add-apt-repository  ppa:chris-lea/redis-server
sudo apt-get update
sudo apt-get install -y redis-server
```

添加videokit到INSTALLED_APPS
```
INSTALLED_APPS = (
    ...
    'videokit',
)
```

然后,
创建项目所在的python虚拟环境
并执行:
```
pip install -r requirements.txt
```

- 配置数据库
在settings.py中配置
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shortvideo',  # 数据库名称
        'USER':'root', # 数据库用户名
        'PASSWORD': 'root',  # 数据库密码
        'HOST': '127.0.0.1', # 数据库主机，留空默认为localhost
        'PORT': 3306, # 数据库端口
    }
}
```
- 根据models生成数据表
```
python manage.py makemigrations
python manage.py migrate
```
note: 如果數據庫操作顯示`no changes`,可先清空每個app下的migrations目錄下除了__init__.py的所有文件,再執行上面兩個命令

- 创建超级用户
```
python manage.py createsuperuser
```

- 运行
```
python manage.py runserver 0.0.0.0:8000
```

#### 问题
1.Redis 报错
```
MISCONF Redis is configured to save RDB snapshots, but is currently not able to persist on disk. Commands that may modify the data set are disabled. Please check Redis logs for details about the error.
```
解决方法:
修改redis配置文件,将stop-writes-on-bgsave-error修改为no
```
sudo vim /etc/redis/redis.conf

```
或者,直接修改
```
config set stop-writes-on-bgsave-error no
```

