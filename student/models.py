from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    # Fix: Corrected on_delete syntax
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    
    # Academic Details
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ssc_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    intermediate_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Professional Info
    skills = models.TextField(help_text="Comma separated skills", blank=True)
    interested_roles = models.CharField(max_length=255, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/%Y/%m/', null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/default_user.png')
    bio = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Profile - {self.user.email}"

class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('interview_pending', 'AI Interview Pending'),
        ('round1', 'Technical Round 1'),
        ('round2', 'Technical Round 2'),
        ('final', 'Final Interview'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    # Link to Recruiter Opportunity (Ensure the 'recruiter' app exists)
    opportunity = models.ForeignKey('recruiter.Opportunity', on_delete=models.CASCADE, related_name='applicants')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_on = models.DateTimeField(auto_now_add=True)
    
    # --- AI INTERVIEW DATA (Phase 2 & 4) ---
    ai_score = models.IntegerField(default=0)
    ai_transcript = models.TextField(blank=True, help_text="Full text-based conversation log")
    ai_behavioral_notes = models.TextField(blank=True, help_text="Insights on confidence, surroundings, etc.")
    is_authentic = models.BooleanField(default=True, help_text="AI check for fake/real interaction")
    
    # Verification indicator for Admin/Recruiter
    is_shortlisted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.email} - {self.opportunity.title}"