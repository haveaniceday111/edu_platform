from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone
from .forms import (CourseChapterForm, LoginForm, CourseResourceForm,
    ActivityForm, CollaborationDiscussionForm, DiscussionReplyForm,
    MeetingRecordForm, AchievementForm, UserRegistrationForm
)
from .models import (User, CourseChapter, CourseResource, Activity, CollaborationDiscussion,
    DiscussionReply, MeetingRecord, Achievement
)

# 超级管理员仪表盘视图
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return HttpResponse("权限不足：只有系统管理员可以访问")
    activity_count = Activity.objects.count()
    discussion_count = CollaborationDiscussion.objects.count()
    user_count = User.objects.count()
    return render(request, "dashboard.html", {
        'user': request.user,
        'role': 'admin',
        'activity_count': activity_count,
        'discussion_count': discussion_count,
        'user_count': user_count
    })

# 学生仪表盘视图
@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return HttpResponse("权限不足：只有学生可以访问")
    resource_count = CourseResource.objects.count()
    active_activities = Activity.objects.filter(status='published')
    discussion_count = CollaborationDiscussion.objects.count()
    return render(request, "dashboard.html", {
        'user': request.user,
        'role': 'student',
        'resource_count': resource_count,
        'active_activities': active_activities,
        'discussion_count': discussion_count
    })

# 教师仪表盘视图
@login_required
def teacher_dashboard(request):
    if request.user.role != "teacher":
        return HttpResponse("权限不足：只有教师可以访问")
    resource_count = CourseResource.objects.filter(teacher=request.user).count()
    my_activities = Activity.objects.filter(creator=request.user)
    my_discussions = CollaborationDiscussion.objects.filter(creator=request.user)
    return render(request, "dashboard.html", {
        'user': request.user,
        'role': 'teacher',
        'resource_count': resource_count,
        'my_activities': my_activities,
        'my_discussions': my_discussions
    })

# 助教仪表盘视图
@login_required
def assistant_dashboard(request):
    if request.user.role != "assistant":
        return HttpResponse("权限不足：只有助教可以访问")
    resource_count = CourseResource.objects.count()
    all_activities = Activity.objects.filter(status='published')
    discussion_count = CollaborationDiscussion.objects.count()
    return render(request, "dashboard.html", {
        'user': request.user,
        'role': 'assistant',
        'resource_count': resource_count,
        'all_activities': all_activities,
        'discussion_count': discussion_count
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role == "assistant":
                return redirect("assistant_dashboard")
            elif user.role == "teacher":
                return redirect("teacher_dashboard")
            else:
                return redirect("student_dashboard")
        else:
            messages.error(request, "账号或密码错误")

    return render(request, "login.html")
    
def logout_view(request):
    logout(request)
    messages.success(request, "您已成功退出登录")
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'student')
        
        if not username or not email or not password1 or not password2:
            messages.error(request, '请填写完整信息')
            return render(request, 'register.html')
        
        if password1 != password2:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '该用户名已被注册')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '该邮箱已被注册')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.role = role
        user.save()
        
        login(request, user)
        messages.success(request, '注册成功！欢迎来到心晴研究所')
        
        if user.role == "admin":
            return redirect("admin_dashboard")
        elif user.role == "assistant":
            return redirect("assistant_dashboard")
        elif user.role == "teacher":
            return redirect("teacher_dashboard")
        else:
            return redirect("student_dashboard")
    
    return render(request, 'register.html')

# 仪表盘视图（根据角色展示不同内容）
@login_required
def dashboard_view(request):
    user = request.user
    
    # 教师统计数据
    if user.role == 'teacher':
        resource_count = CourseResource.objects.filter(teacher=user).count()
        my_activities = Activity.objects.filter(creator=user)
        my_discussions = CollaborationDiscussion.objects.filter(creator=user)
        context = {
            'user': user,
            'role': user.role,
            'resource_count': resource_count,
            'my_activities': my_activities,
            'my_discussions': my_discussions,
        }
    
    # 学生统计数据
    elif user.role == 'student':
        all_resources = CourseResource.objects.all()
        active_activities = Activity.objects.filter(status='published', 
                                                   start_time__lte=timezone.now(),
                                                   end_time__gte=timezone.now())
        all_discussions = CollaborationDiscussion.objects.all()
        context = {
            'user': user,
            'role': user.role,
            'all_resources': all_resources,
            'active_activities': active_activities,
            'all_discussions': all_discussions,
        }
    
    # 管理员统计数据
    else:  # admin
        all_activities = Activity.objects.all()
        all_discussions = CollaborationDiscussion.objects.all()
        all_users = User.objects.all()
        context = {
            'user': user,
            'role': user.role,
            'all_activities': all_activities,
            'all_discussions': all_discussions,
            'all_users': all_users,
        }
    
    return render(request, 'dashboard.html', context)

# -------------------------- 课程资源库视图 --------------------------
# 课时目录编辑页（教师上传资源的第一步）
@login_required
def chapter_manage_view(request):
    # 仅教师可访问
    if request.user.role != 'teacher':
        return HttpResponseForbidden('仅教师可编辑课时目录！')
    
    # 获取当前教师的所有课时
    chapters = CourseChapter.objects.filter(teacher=request.user)
    
    # 新增/编辑课时
    if request.method == 'POST':
        chapter_id = request.POST.get('chapter_id')
        if chapter_id:  # 编辑已有课时
            chapter = get_object_or_404(CourseChapter, id=chapter_id, teacher=request.user)
            form = CourseChapterForm(request.POST, instance=chapter)
        else:  # 新增课时
            form = CourseChapterForm(request.POST)
            form.instance.teacher = request.user
        
        if form.is_valid():
            form.save()
            messages.success(request, '课时编辑成功！')
            return redirect('chapter_manage')
    
    # 删除课时
    if request.method == 'GET' and 'delete' in request.GET:
        chapter_id = request.GET.get('delete')
        chapter = get_object_or_404(CourseChapter, id=chapter_id, teacher=request.user)
        chapter.delete()
        messages.success(request, '课时删除成功！')
        return redirect('chapter_manage')
    
    # 空表单（新增课时用）
    form = CourseChapterForm()
    
    context = {
        'chapters': chapters,
        'form': form,
    }
    return render(request, 'chapter_manage.html', context)

# ------------------------ 新增：资源上传视图 ------------------------
# 按课时上传资源（教师选择课时后进入此页面）
@login_required
def resource_upload_view(request, chapter_id=None):
    if request.user.role != 'teacher':
        return HttpResponseForbidden('仅教师可上传资源！')
    
    # 获取目标课时（如果传了chapter_id）
    chapter = None
    if chapter_id:
        chapter = get_object_or_404(CourseChapter, id=chapter_id, teacher=request.user)
    
    if request.method == 'POST':
        form = CourseResourceForm(request.POST, request.FILES)
        form.instance.teacher = request.user  # 关联当前教师
        if chapter:
            form.instance.chapter = chapter  # 关联选中的课时
        
        if form.is_valid():
            form.save()
            messages.success(request, '资源上传成功！')
            return redirect('resource_list')  # 上传后跳转到资源列表
    else:
        # 初始化表单，默认选中传入的课时
        initial_data = {'chapter': chapter} if chapter else {}
        form = CourseResourceForm(initial=initial_data)
    
    # 获取当前教师的所有课时（供表单选择）
    chapters = CourseChapter.objects.filter(teacher=request.user)
    
    context = {
        'form': form,
        'chapters': chapters,
        'current_chapter': chapter,
    }
    return render(request, 'resource_upload.html', context)

# ------------------------ 新增：资源查看视图 ------------------------
# 教师查看自己上传的资源（按课时分组）
@login_required
def resource_list_view(request):
    if request.user.role == 'teacher':
        # 教师：查看自己的所有课时+对应资源
        chapters = CourseChapter.objects.filter(teacher=request.user)
        # 预加载资源，减少数据库查询
        chapters = chapters.prefetch_related('resources')
    elif request.user.role == 'student':
        # 学生：查看所有教师发布的资源（可后续限制为自己的任课教师）
        chapters = CourseChapter.objects.all().prefetch_related('resources')
    else:
        # 管理员：查看所有资源
        chapters = CourseChapter.objects.all().prefetch_related('resources')
    
    context = {
        'chapters': chapters,
        'user_role': request.user.role,
    }
    return render(request, 'resource_list.html', context)

# ------------------------ 新增：资源编辑视图 ------------------------
@login_required
def resource_update_view(request, pk):
    resource = get_object_or_404(CourseResource, pk=pk)
    # 只有上传者或管理员可以编辑
    if request.user != resource.teacher and request.user.role != 'admin':
        messages.error(request, '无权限编辑该资源')
        return redirect('resource_list')
    
    if request.method == 'POST':
        form = CourseResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, '资源更新成功！')
            return redirect('resource_list')
    else:
        form = CourseResourceForm(instance=resource)
    
    # 获取当前教师的所有课时
    chapters = CourseChapter.objects.filter(teacher=request.user)
    
    context = {
        'form': form,
        'chapters': chapters,
        'resource': resource,
    }
    return render(request, 'resource_update.html', context)

# ------------------------ 新增：资源删除视图 ------------------------
@login_required
def resource_delete_view(request, pk):
    resource = get_object_or_404(CourseResource, pk=pk)
    # 只有上传者或管理员可以删除
    if request.user != resource.teacher and request.user.role != 'admin':
        messages.error(request, '无权限删除该资源')
        return redirect('resource_list')
    
    if request.method == 'POST':
        resource.delete()
        messages.success(request, '资源删除成功！')
        return redirect('resource_list')
    return render(request, 'resource_delete.html', {'resource': resource})

# -------------------------- 活动管理视图 --------------------------
# 活动列表
@login_required
def activity_list_view(request):
    if request.user.role == 'student':
        activities = Activity.objects.filter(status='published')
    elif request.user.role == 'teacher':
        activities = Activity.objects.filter(creator=request.user)
    else:  # admin
        activities = Activity.objects.all()
    return render(request, 'activities/list.html', {'activities': activities})

# 创建活动（教师/管理员）
@login_required
def activity_create_view(request):
    if request.user.role == 'student':
        messages.error(request, '仅教师和管理员可创建活动')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.creator = request.user
            activity.save()
            messages.success(request, '活动创建成功！')
            return redirect('activity_list')
    else:
        form = ActivityForm()
    return render(request, 'activities/create.html', {'form': form})

# 编辑活动（创建者/管理员）
@login_required
def activity_update_view(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.user != activity.creator and request.user.role != 'admin':
        messages.error(request, '无权限编辑该活动')
        return redirect('activity_list')
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, '活动更新成功！')
            return redirect('activity_list')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'activities/update.html', {'form': form, 'activity': activity})

# 删除活动（创建者/管理员）
@login_required
def activity_delete_view(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.user != activity.creator and request.user.role != 'admin':
        messages.error(request, '无权限删除该活动')
        return redirect('activity_list')
    
    if request.method == 'POST':
        activity.delete()
        messages.success(request, '活动删除成功！')
        return redirect('activity_list')
    return render(request, 'activities/delete.html', {'activity': activity})

# -------------------------- 协作空间视图 --------------------------
# 讨论列表
@login_required
def discussion_list_view(request):
    discussions = CollaborationDiscussion.objects.all().order_by('-created_at')
    return render(request, 'collaboration/discussions/list.html', {'discussions': discussions})

# 创建讨论（教师/管理员）
@login_required
def discussion_create_view(request):
    if request.method == 'POST':
        form = CollaborationDiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.creator = request.user
            discussion.save()
            messages.success(request, '讨论创建成功！')
            return redirect('discussion_list')
    else:
        form = CollaborationDiscussionForm()
    return render(request, 'collaboration/discussions/create.html', {'form': form})

# 讨论详情（含回复）
@login_required
def discussion_detail_view(request, pk):
    discussion = get_object_or_404(CollaborationDiscussion, pk=pk)
    replies = discussion.replies.all().order_by('created_at')
    
    if request.method == 'POST':
        form = DiscussionReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = discussion
            reply.author = request.user
            reply.save()
            messages.success(request, '回复成功！')
            return redirect('discussion_detail', pk=pk)
    else:
        form = DiscussionReplyForm()
    
    return render(request, 'collaboration/discussions/detail.html', {
        'discussion': discussion,
        'replies': replies,
        'form': form
    })

# 编辑讨论（创建者/管理员）
@login_required
def discussion_update_view(request, pk):
    discussion = get_object_or_404(CollaborationDiscussion, pk=pk)
    if request.user != discussion.creator and request.user.role != 'admin':
        messages.error(request, '无权限编辑该讨论')
        return redirect('discussion_list')
    
    if request.method == 'POST':
        form = CollaborationDiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            messages.success(request, '讨论更新成功！')
            return redirect('discussion_detail', pk=pk)
    else:
        form = CollaborationDiscussionForm(instance=discussion)
    return render(request, 'collaboration/discussions/update.html', {'form': form, 'discussion': discussion})

# 删除讨论（创建者/管理员）
@login_required
def discussion_delete_view(request, pk):
    discussion = get_object_or_404(CollaborationDiscussion, pk=pk)
    if request.user != discussion.creator and request.user.role != 'admin':
        messages.error(request, '无权限删除该讨论')
        return redirect('discussion_list')
    
    if request.method == 'POST':
        discussion.delete()
        messages.success(request, '讨论删除成功！')
        return redirect('discussion_list')
    return render(request, 'collaboration/discussions/delete.html', {'discussion': discussion})

# 会议记录管理
@login_required
def meeting_record_list_view(request):
    records = MeetingRecord.objects.all().order_by('-meeting_date')
    return render(request, 'collaboration/meetings/list.html', {'records': records})

@login_required
def meeting_record_create_view(request):
    if request.user.role == 'student':
        messages.error(request, '仅教师和管理员可创建会议记录')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MeetingRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorder = request.user
            record.save()
            messages.success(request, '会议记录创建成功！')
            return redirect('meeting_record_list')
    else:
        form = MeetingRecordForm()
    return render(request, 'collaboration/meetings/create.html', {'form': form})

# 成果展示管理
@login_required
def achievement_list_view(request):
    achievements = Achievement.objects.all().order_by('-created_at')
    return render(request, 'collaboration/achievements/list.html', {'achievements': achievements})

@login_required
def achievement_create_view(request):
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.creator = request.user
            achievement.save()
            messages.success(request, '成果展示创建成功！')
            return redirect('achievement_list')
    else:
        form = AchievementForm()
    return render(request, 'collaboration/achievements/create.html', {'form': form})