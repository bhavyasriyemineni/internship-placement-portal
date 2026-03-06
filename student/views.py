from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json

# Internal App Imports
from .models import StudentProfile, Application
from recruiter.models import Opportunity 
from accounts.models import Notification  # Corrected Import
from core.ai_utils import InterviewEngine

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('dashboard_redirect')
        
    apps = Application.objects.filter(student=request.user)
    # Use get_or_create to prevent errors if profile doesn't exist yet
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # Refined completion logic (Feature: Profile Completion Status Indicator)
    fields_to_check = [profile.cgpa, profile.skills, profile.resume, profile.ssc_percentage, profile.bio]
    filled = [f for f in fields_to_check if f]
    completion = int((len(filled) / len(fields_to_check)) * 100)

    context = {
        'total_apps': apps.count(),
        'interviews': apps.filter(status__in=['round1', 'round2', 'final']).count(),
        'selected': apps.filter(status='selected').count(),
        'profile_strength': completion,
        'recent_applications': apps.order_by('-applied_on')[:5],
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def profile_view(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, 'student/profile_view.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.cgpa = request.POST.get('cgpa')
        profile.ssc_percentage = request.POST.get('ssc')
        profile.intermediate_percentage = request.POST.get('inter')
        profile.skills = request.POST.get('skills')
        profile.interested_roles = request.POST.get('roles')
        profile.bio = request.POST.get('bio')
        
        if request.FILES.get('resume'):
            profile.resume = request.FILES.get('resume')
            
        profile.save()
        messages.success(request, "Professional profile updated successfully!")
        return redirect('student_profile')
    return render(request, 'student/profile_edit.html', {'profile': profile})

@login_required
def opportunity_list(request):
    # Only show active opportunities
    opportunities = Opportunity.objects.filter(is_active=True).order_by('-created_at')
    query = request.GET.get('q')
    if query:
        opportunities = opportunities.filter(title__icontains=query)
    return render(request, 'student/opportunity_list.html', {'opportunities': opportunities})

@login_required
def apply_opportunity(request, opp_id):
    opportunity = get_object_or_404(Opportunity, id=opp_id)
    
    if Application.objects.filter(student=request.user, opportunity=opportunity).exists():
        messages.warning(request, "You have already applied for this position.")
    else:
        # Create application (Feature: Application Status Update Notification)
        Application.objects.create(student=request.user, opportunity=opportunity)
        messages.success(request, f"Application for {opportunity.title} submitted successfully!")
        
    return redirect('my_applications')

@login_required
def my_applications(request):
    apps = Application.objects.filter(student=request.user).order_by('-applied_on')

    steps = ["Applied", "Round 1", "Round 2", "Final"]

    return render(
        request,
        'student/my_applications.html',
        {
            'applications': apps,
            'steps': steps
        }
    )


@login_required
def application_detail(request, app_id):
    # Security check: Ensure student owns the application
    application = get_object_or_404(Application, id=app_id, student=request.user)
    return render(request, 'student/application_detail.html', {'app': application})

# --- AI Mock Interview Views (Phase 2 & 4) ---

@login_required
def ai_interview_intro(request):
    applications = Application.objects.filter(student=request.user)

    return render(
        request,
        'student/ai_interview_start.html',
        {
            'applications': applications
        }
    )


@login_required
def ai_interview_report(request, app_id):
    application = get_object_or_404(Application, id=app_id, student=request.user)
    # Ensure interview has been completed before showing report
    if not application.ai_score:
        messages.info(request, "AI Interview report is not yet generated.")
        return redirect('my_applications')
    return render(request, 'student/ai_interview_report.html', {'app': application})

@login_required
def ai_mock_interview(request, app_id):
    application = get_object_or_404(Application, id=app_id, student=request.user)

    # Placeholder logic for AI interview session
    # Later you can integrate OpenAI / scoring system here

    return render(request, 'student/ai_mock_interview.html', {
        'application': application
    })

@login_required
def notification_list(request):
    """
    Universal Notification Center.
    Differentiates shell (sidebar/header) based on User Role.
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # 🧠 Logic to determine which "Base" to extend
    # If the user is a student, use student base. Otherwise, use recruiter base.
    base_template = 'base_student.html' if request.user.role == 'student' else 'base_recruiter.html'
    
    return render(request, 'shared/notifications.html', {
        'notifications': notifications,
        'base_template': base_template
    })

@login_required
def mark_all_notifications_read(request):
    """Marks all unread alerts as read and redirects back to the list."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Inbox cleared successfully.")
    return redirect('notification_list')

@login_required
def process_ai_interview(request):
    """
    Background AJAX view that communicates with Gemini API.
    Handles real-time conversation and final scoring.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body)
        user_text = data.get('answer')
        app_id = data.get('application_id')
        behavioral = data.get('behavioral', {})
        is_last = data.get('is_last', False) 

        application = get_object_or_404(Application, id=app_id, student=request.user)
        
        # Initialize Engine with Student Context
        engine = InterviewEngine(
            student_name=request.user.username,
            target_role=application.opportunity.title,
            skills=request.user.student_profile.skills
        )

        if is_last:
            # 🏆 FINAL STEP: Summarize session and generate report
            report_data = engine.generate_final_report()
            application.ai_score = report_data.get('score', 0)
            application.ai_behavioral_notes = report_data.get('summary', "No notes.")
            application.save()
            
            return JsonResponse({
                'is_finished': True,
                'redirect_url': f'/student/ai-interview/report/{app_id}/'
            })

        # CONTINUE CONVERSATION: Get next adaptive question from Gemini
        ai_response = engine.get_next_question(user_text, behavioral)

        # SECURITY: Check for Red Flags in behavioral data
        if behavioral.get('faces_detected', 1) > 1 or behavioral.get('looking_away'):
            application.is_authentic = False 
            application.save()

        return JsonResponse({
            'question': ai_response,
            'is_finished': False
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_text = data.get('answer')
            app_id = data.get('application_id')
            behavioral = data.get('behavioral')
            is_last = data.get('is_last', False) # Critical for 100% completion

            application = get_object_or_404(Application, id=app_id, student=request.user)
            
            # Initialize Engine
            engine = InterviewEngine(
                student_name=request.user.username,
                target_role=application.opportunity.title,
                skills=request.user.student_profile.skills
            )

            if is_last:
                # 🏆 Final Step: Generate and Save Report
                report_data = engine.generate_final_report()
                application.ai_score = report_data.get('score', 0)
                application.ai_behavioral_notes = report_data.get('summary', "")
                application.is_authentic = report_data.get('is_authentic', True)
                application.save()
                
                return JsonResponse({
                    'is_finished': True,
                    'redirect_url': f'/student/ai-interview/report/{app_id}/'
                })

            # Continue conversation
            next_q = engine.get_next_question(user_text, behavioral)
            return JsonResponse({
                'question': next_q,
                'is_finished': False
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
    """
    Background AJAX view that communicates with Gemini API.
    Receives: Student's spoken text & behavioral data.
    Returns: Next AI question & session status.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_text = data.get('answer')
            app_id = data.get('application_id')
            behavioral = data.get('behavioral')

            # 1. Fetch the application context
            application = get_object_or_404(Application, id=app_id, student=request.user)
            
            # 2. Initialize the AI Engine with Student Context
            # Note: In a production app, you'd store chat history in sessions
            engine = InterviewEngine(
                student_name=request.user.username,
                target_role=application.opportunity.title,
                skills=request.user.student_profile.skills
            )

            # 3. Get adaptive question from Gemini
            ai_response = engine.get_next_question(user_text, behavioral)

            # 4. (Optional) Check for Red Flags in behavioral data
            if behavioral.get('faces_detected', 1) > 1 or behavioral.get('looking_away'):
                application.is_authentic = False # Flag for Recruiter/Admin
                application.save()

            return JsonResponse({
                'question': ai_response,
                'is_finished': False
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)