from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RecruiterProfile, Opportunity
from student.models import Application
from django.db.models import Count

@login_required
def recruiter_dashboard(request):
    profile = get_object_or_404(RecruiterProfile, user=request.user)
    my_opportunities = Opportunity.objects.filter(recruiter=profile)
    
    # Logic to count applicants who have completed the AI interview
    from student.models import Application
    ai_verified_count = Application.objects.filter(
        opportunity__recruiter=profile, 
        ai_score__isnull=False  # This ensures they have a score
    ).count()

    context = {
        'total_postings': my_opportunities.count(),
        'total_applicants': Application.objects.filter(opportunity__recruiter=profile).count(),
        'shortlisted_count': Application.objects.filter(opportunity__recruiter=profile, is_shortlisted=True).count(),
        'ai_verified_count': ai_verified_count, # MUST MATCH TEMPLATE VARIABLE
        'recent_postings': my_opportunities.order_by('-created_at')[:5],
    }
    return render(request, 'recruiter/dashboard.html', context)

@login_required
def post_opportunity(request):
    """
    Feature 3: Job / Internship Posting.
    Handles Creation of new training opportunities.
    """
    profile = get_object_or_404(RecruiterProfile, user=request.user)
    
    if request.method == 'POST':
        Opportunity.objects.create(
            recruiter=profile,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            eligibility_criteria=request.POST.get('criteria'),
            required_skills=request.POST.get('skills'),
            min_cgpa=request.POST.get('cgpa', 0.0),
            location=request.POST.get('location', 'Remote'),
            deadline=request.POST.get('deadline')
        )
        messages.success(request, "New opportunity has been published successfully!")
        return redirect('my_postings')
        
    return render(request, 'recruiter/post_opportunity.html')

@login_required
def my_postings(request):
    """
    View to Manage Postings (Edit/Delete placeholder).
    Lists all opportunities created by the recruiter.
    """
    profile = get_object_or_404(RecruiterProfile, user=request.user)
    postings = Opportunity.objects.filter(recruiter=profile).order_by('-created_at')
    return render(request, 'recruiter/my_postings.html', {'postings': postings})

@login_required
def applicant_list(request, opp_id):
    """
    Feature 3: Application Management.
    Lists all students who applied for a specific opportunity, ranked by AI Score.
    """
    opportunity = get_object_or_404(Opportunity, id=opp_id, recruiter__user=request.user)
    applicants = Application.objects.filter(opportunity=opportunity).order_by('-ai_score')
    
    return render(request, 'recruiter/applicant_list.html', {
        'applicants': applicants, 
        'opportunity': opportunity
    })

@login_required
def applicant_detail(request, app_id):
    """
    Feature 3: AI Insight Viewing.
    Provides deep dive into Student Profile and AI Interview Summary/Score.
    """
    application = get_object_or_404(Application, id=app_id, opportunity__recruiter__user=request.user)
    return render(request, 'recruiter/applicant_detail.html', {'app': application})

@login_required
def update_application_status(request, app_id):
    """
    Logic to Shortlist, Reject, or Schedule Interviews.
    Triggers 'Application Status Update' notification for students.
    """
    application = get_object_or_404(Application, id=app_id, opportunity__recruiter__user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        application.status = new_status
        
        # Internal logic: If moved to any round beyond 'applied', mark as shortlisted
        if new_status in ['round1', 'round2', 'final', 'selected']:
            application.is_shortlisted = True
        elif new_status == 'rejected':
            application.is_shortlisted = False
            
        application.save()
        messages.success(request, f"Status for {application.student.username} updated to {application.get_status_display()}.")
        
    return redirect('applicant_detail', app_id=app_id)

@login_required
def company_profile_edit(request):
    """
    Feature 3: Company Profile Management.
    Updates industrial identity and contact details.
    """
    profile, created = RecruiterProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.company_name = request.POST.get('company_name')
        profile.industry = request.POST.get('industry')
        profile.location = request.POST.get('location')
        profile.description = request.POST.get('description')
        profile.contact_email = request.POST.get('contact_email')
        
        if request.FILES.get('logo'):
            profile.company_logo = request.FILES.get('logo')
            
        profile.save()
        messages.success(request, "Company corporate profile updated.")
        return redirect('recruiter_dashboard')
        
    return render(request, 'recruiter/company_profile_edit.html', {'profile': profile})



@login_required
def delete_opportunity(request, opp_id):
    # 1. Fetch the RecruiterProfile associated with the logged-in User
    recruiter_profile = get_object_or_404(RecruiterProfile, user=request.user)
    
    # 2. Security: Ensure the opportunity belongs to THIS profile
    opportunity = get_object_or_404(Opportunity, id=opp_id, recruiter=recruiter_profile)
    
    # 3. Perform Deletion
    opportunity.delete()
    messages.success(request, "Industrial opportunity has been successfully removed.")
    
    return redirect('my_postings')