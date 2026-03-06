from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Profile Management
    path('profile/', views.profile_view, name='student_profile'),
    path('profile/edit/', views.profile_edit, name='student_profile_edit'),
    
    # Internship Opportunities
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('apply/<int:opp_id>/', views.apply_opportunity, name='apply_opportunity'),
    path('ai-interview/process/', views.process_ai_interview, name='process_ai_interview'),
    # Application Tracking
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:app_id>/detail/', views.application_detail, name='application_detail'),
    
    # AI Interview Module
    path('ai-interview/start/', views.ai_interview_intro, name='ai_interview_intro'),
    path('ai-interview/session/<int:app_id>/', views.ai_mock_interview, name='ai_mock_interview'),
    path('ai-interview/report/<int:app_id>/', views.ai_interview_report, name='ai_interview_report'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/', views.mark_all_notifications_read, name='mark_all_read'),
]