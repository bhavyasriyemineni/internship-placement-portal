from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class RecruiterProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )

    company_name = models.CharField(max_length=255)
    industry = models.CharField(
        max_length=100,
        help_text="e.g. Software, Finance, Manufacturing"
    )
    location = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        help_text="Brief about the company"
    )
    contact_email = models.EmailField()
    company_logo = models.ImageField(
        upload_to='logos/',
        default='logos/default_company.png'
    )
    website = models.URLField(blank=True)

    def __str__(self):
        return self.company_name


class Opportunity(models.Model):
    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    eligibility_criteria = models.TextField(
        help_text="Education, year of passing, etc."
    )
    required_skills = models.TextField(
        help_text="Comma separated skills"
    )

    min_cgpa = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    default=7.5,
    validators=[MinValueValidator(7.5)]
    )
    deadline = models.DateTimeField()
    location = models.CharField(
        max_length=255,
        default="Remote"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.recruiter.company_name}"
