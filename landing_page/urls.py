from django.urls import path
from .views import PostListView , PostDetailView, PostCreateView , PostUpdateView , PostDeleteView , UserPostListView
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='landing-page-home'),
    path('portfolio/', views.portfolio, name='landing-portfolio'),
    path('privacy-policy', views.privacy_policy, name='privacy-policy'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), 
    path('about/', views.about, name='landing-page-about'),
    path('blog/', PostListView.as_view(), name='blog'),
    path('blog/post/new/', PostCreateView.as_view(), name='post-create'),
    path('blog/post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('blog/post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('blog/post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    
    
    # Add other URLs as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
