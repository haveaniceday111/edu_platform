from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import os

# 自定义用户模型（区分角色）
class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', '教师'),
        ('student', '学生'),
        ('assistant', '助教'),
        ('admin', '管理员'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

# ------------------------ 新增：课时/章节模型（CourseChapter） ------------------------
class CourseChapter(models.Model):
    # 关联创建该课时的教师（外键）
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapters')
    # 课时标题（如“01Java概述”）
    title = models.CharField(max_length=100, verbose_name='课时标题')
    # 排序号（控制课时展示顺序，数字越小越靠前）
    order = models.IntegerField(default=0, verbose_name='排序号')
    # 创建时间（自动生成）
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '课程课时'       # 后台显示的单名
        verbose_name_plural = '课程课时' # 后台显示的复数名
        ordering = ['order']            # 按排序号升序展示
        unique_together = ['teacher', 'title']  # 同一教师的课时标题不重复（避免重复创建）

    def __str__(self):
        return f"{self.teacher.username} - {self.title}"

# ------------------------ 重写：课程资源模型（CourseResource） ------------------------
# 替换原有简单的CourseResource，新增资源类型、关联课时等功能
class CourseResource(models.Model):
    # 资源类型枚举（对应不同标识）
    RESOURCE_TYPES = (
        ('document', '文档/课件'),    # 如PPT、PDF、Word
        ('install', '安装包/工具'),   # 如JDK、编辑器安装包
        ('link', '链接/地址'),        # 如下载地址、API文档链接
        ('other', '其他资源'),
    )
    # 关联所属课时（外键，删除课时时同步删除资源）
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='resources')
    # 关联上传该资源的教师（外键）
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    # 资源名称（如“JDK下载地址”）
    title = models.CharField(max_length=200, verbose_name='资源名称')
    # 资源类型（选择框）
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='document', verbose_name='资源类型')
    # 本地文件（上传文件用，链接类资源可空）
    file = models.FileField(upload_to='course_resources/', blank=True, null=True, verbose_name='上传文件')
    # 链接地址（非文件类资源用，文件类资源可空）
    link = models.URLField(blank=True, null=True, verbose_name='资源链接')
    # 开始时间/有效期（可选）
    start_time = models.DateTimeField(blank=True, null=True, verbose_name='开始时间/有效期')
    # 创建时间（自动生成）
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = '课程资源'
        ordering = ['-created_at']  # 按创建时间倒序展示（最新上传的在前）

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

    # ------------------------ 新增：自定义方法（前端展示用） ------------------------
    # 1. 获取资源展示的图标样式（对应前端不同类型的图标）
    def get_icon_class(self):
        icon_map = {
            'document': 'bi bi-file-earmark-text text-secondary',  # 文档图标（灰色）
            'install': 'bi bi-box-seam text-warning',              # 安装包图标（黄色）
            'link': 'bi bi-link-45deg text-primary',               # 链接图标（蓝色）
            'other': 'bi bi-file-earmark text-dark',               # 其他图标（黑色）
        }
        return icon_map.get(self.resource_type, 'bi bi-file-earmark text-dark')
    
    # 2. 获取资源类型的中文标签（带样式）
    def get_type_label(self):
        label_map = {
            'document': '<span class="badge bg-secondary">文档/课件</span>',
            'install': '<span class="badge bg-warning">安装包/工具</span>',
            'link': '<span class="badge bg-primary">链接/地址</span>',
            'other': '<span class="badge bg-dark">其他</span>',
        }
        return label_map.get(self.resource_type, '<span class="badge bg-dark">其他</span>')
    
    # 3. 获取资源访问地址（文件/链接二选一）
    def get_resource_url(self):
        if self.link:
            return self.link  # 链接类资源返回链接
        elif self.file:
            return self.file.url  # 文件类资源返回文件下载地址
        return '#'  # 无资源时返回空链接
    
    # 4. 重写删除方法：删除资源时同步删除服务器上的文件
    def delete(self, *args, **kwargs):
        # 如果有上传的文件，先删除服务器上的文件
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        # 再执行默认的删除操作
        super().delete(*args, **kwargs)

# 活动模型
class Activity(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('ended', '已结束'),
    )
    title = models.CharField(max_length=200, verbose_name='活动标题')
    content = models.TextField(verbose_name='活动内容')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               limit_choices_to={'role__in': ['teacher', 'admin']}, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '活动'
        verbose_name_plural = '活动'
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'published'

# 协作讨论模型
class CollaborationDiscussion(models.Model):
    title = models.CharField(max_length=200, verbose_name='讨论标题')
    content = models.TextField(verbose_name='讨论内容')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_pinned = models.BooleanField(default=False, verbose_name='是否置顶')
    
    class Meta:
        verbose_name = '协作讨论'
        verbose_name_plural = '协作讨论'
    
    def __str__(self):
        return self.title

# 讨论回复模型
class DiscussionReply(models.Model):
    discussion = models.ForeignKey(CollaborationDiscussion, on_delete=models.CASCADE, 
                                  related_name='replies', verbose_name='所属讨论')
    content = models.TextField(verbose_name='回复内容')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='回复者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='回复时间')
    
    class Meta:
        verbose_name = '讨论回复'
        verbose_name_plural = '讨论回复'
    
    def __str__(self):
        return f'回复 {self.discussion.title} - {self.author.username}'

# 会议记录模型
class MeetingRecord(models.Model):
    title = models.CharField(max_length=200, verbose_name='会议标题')
    content = models.TextField(verbose_name='会议内容')
    meeting_date = models.DateTimeField(verbose_name='会议时间')
    recorder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                limit_choices_to={'role__in': ['teacher', 'admin']}, verbose_name='记录人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '会议记录'
        verbose_name_plural = '会议记录'
    
    def __str__(self):
        return self.title

# 成果展示模型
class Achievement(models.Model):
    title = models.CharField(max_length=200, verbose_name='成果标题')
    content = models.TextField(verbose_name='成果内容')
    file = models.FileField(upload_to='achievements/%Y/%m/%d/', blank=True, null=True, verbose_name='成果附件')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '成果展示'
        verbose_name_plural = '成果展示'
    
    def __str__(self):
        return self.title