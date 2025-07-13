from django.contrib import admin
from .models import Post , PageVisit , NewsletterSubscription

admin.site.register(NewsletterSubscription)
admin.site.register(Post)
admin.site.register(PageVisit)
