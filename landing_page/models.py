from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    attached = models.FileField(upload_to='post_files', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    visibility = models.IntegerField(default=1)

    def __str__(self):
        return self.title 
    
    def get_absolute_url(self):
        return reverse('post-detail',kwargs={'pk':self.pk})
    
    class Meta:
        permissions = [
            ("can_view_blog", "Can view blog"),
        ]


class PageVisit(models.Model):
    home_visit_count = models.IntegerField(default=0)
    portfolio_visit_count = models.IntegerField(default=0)
    about_visit_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Home Visits: {self.home_visit_count} , Portfolio Visits: {self.portfolio_visit_count} , About Visits: {self.about_visit_count}"


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
