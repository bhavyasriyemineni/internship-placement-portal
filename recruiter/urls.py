from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    
    # Profile Management
    path('profile/edit/', views.company_profile_edit, name='company_profile_edit'),
    
    # Internship / Training Posting
    path('post-opportunity/', views.post_opportunity, name='post_opportunity'),
    path('my-postings/', views.my_postings, name='my_postings'),
    
    # Applicant Management & AI Insights
    path('applicants/<int:opp_id>/', views.applicant_list, name='applicant_list'),
    path('applicant/<int:app_id>/detail/', views.applicant_detail, name='applicant_detail'),
    path('opportunity/<int:opp_id>/delete/', views.delete_opportunity, name='delete_opportunity'),
    
    # Status & Selection
    path('update-status/<int:app_id>/', views.update_application_status, name='update_status'),
]