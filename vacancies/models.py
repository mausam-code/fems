from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class Company(models.Model):
    name = models.CharField(_('Company Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='company_logos/', blank=True, null=True)
    address = models.TextField(_('Address'), blank=True)
    contact_email = models.EmailField(_('Contact Email'), blank=True)
    contact_phone = models.CharField(_('Contact Phone'), max_length=20, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class JobCategory(models.Model):
    name = models.CharField(_('Category Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    
    class Meta:
        verbose_name = _('Job Category')
        verbose_name_plural = _('Job Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(_('Country Name'), max_length=100)
    code = models.CharField(_('Country Code'), max_length=3)
    
    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(_('Skill Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    
    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Vacancy(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('open', _('Open')),
        ('closed', _('Closed')),
        ('filled', _('Filled')),
    )
    
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', _('Full Time')),
        ('part_time', _('Part Time')),
        ('contract', _('Contract')),
        ('temporary', _('Temporary')),
        ('seasonal', _('Seasonal')),
        ('internship', _('Internship')),
    )
    
    title = models.CharField(_('Job Title'), max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='vacancies')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='vacancies')
    location = models.CharField(_('Location'), max_length=255)
    description = models.TextField(_('Job Description'))
    requirements = models.TextField(_('Requirements'))
    responsibilities = models.TextField(_('Responsibilities'))
    benefits = models.TextField(_('Benefits'), blank=True)
    salary_min = models.DecimalField(_('Minimum Salary'), max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(_('Maximum Salary'), max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(_('Currency'), max_length=3, default='USD')
    is_salary_visible = models.BooleanField(_('Display Salary'), default=True)
    employment_type = models.CharField(_('Employment Type'), max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    experience_required = models.PositiveIntegerField(_('Experience Required (years)'), default=0)
    education_required = models.CharField(_('Education Required'), max_length=255, blank=True)
    skills_required = models.ManyToManyField(Skill, related_name='vacancies', blank=True)
    application_deadline = models.DateField(_('Application Deadline'), null=True, blank=True)
    posted_date = models.DateField(_('Posted Date'), default=timezone.now)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(_('Featured'), default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_vacancies'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='updated_vacancies'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Vacancy')
        verbose_name_plural = _('Vacancies')
        ordering = ['-posted_date', '-is_featured']
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    @property
    def is_open(self):
        return self.status == 'open' and (not self.application_deadline or self.application_deadline >= timezone.now().date())

class VacancyAttachment(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(_('Title'), max_length=255)
    file = models.FileField(_('File'), upload_to='vacancy_attachments/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='uploaded_vacancy_attachments'
    )
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Vacancy Attachment')
        verbose_name_plural = _('Vacancy Attachments')
    
    def __str__(self):
        return self.title
