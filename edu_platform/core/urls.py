from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('assistant_dashboard/', views.assistant_dashboard, name='assistant_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    # 其他你现有的路由
    # 新增：课时管理（教师上传资源第一步）
    path('chapters/manage/', views.chapter_manage_view, name='chapter_manage'),
    # 新增：资源上传（可选指定课时）
    path('resources/upload/', views.resource_upload_view, name='resource_upload'),
    path('resources/upload/<int:chapter_id>/', views.resource_upload_view, name='resource_upload_chapter'),
    # 新增：资源查看
    path('resources/list/', views.resource_list_view, name='resource_list'),
    # 新增：资源编辑/删除
    path('resources/<int:pk>/update/', views.resource_update_view, name='resource_update'),
    path('resources/<int:pk>/delete/', views.resource_delete_view, name='resource_delete'),

    
    # 活动管理

    path('activities/', views.activity_list_view, name='activity_list'),
    path('activities/create/', views.activity_create_view, name='activity_create'),
    path('activities/<int:pk>/update/', views.activity_update_view, name='activity_update'),
    path('activities/<int:pk>/delete/', views.activity_delete_view, name='activity_delete'),
    
    # 协作空间 - 讨论
    path('discussions/', views.discussion_list_view, name='discussion_list'),
    path('discussions/create/', views.discussion_create_view, name='discussion_create'),
    path('discussions/<int:pk>/', views.discussion_detail_view, name='discussion_detail'),
    path('discussions/<int:pk>/update/', views.discussion_update_view, name='discussion_update'),
    path('discussions/<int:pk>/delete/', views.discussion_delete_view, name='discussion_delete'),
    
    # 协作空间 - 会议记录
    path('meetings/', views.meeting_record_list_view, name='meeting_record_list'),
    path('meetings/create/', views.meeting_record_create_view, name='meeting_record_create'),
    
    # 协作空间 - 成果展示
    path('achievements/', views.achievement_list_view, name='achievement_list'),
    path('achievements/create/', views.achievement_create_view, name='achievement_create'),
]