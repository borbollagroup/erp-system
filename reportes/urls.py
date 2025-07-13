# reportes/urls.py
from django.urls import path
from .views import daily_report, DailyReportDetailView, DailyReportUpdateView , daily_report_list ,client_list, client_create, client_edit, client_delete, client_upsert, ProjectCreateView, ProjectUpdateView,client_contacts_json
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth import views as auth_views




from .views import (
    ProjectListView,
    ProjectListJsonView,
    ProjectDeleteView,
    daily_report, 
    DailyReportDetailView, 
    DailyReportUpdateView , 
    daily_report_list,
    FullDailyReportListView,
    logout_view,
    export_project_reports,
    import_daily_reports
)


app_name = 'reportes'

superuser_required = user_passes_test(lambda u: u.is_superuser)

urlpatterns = [
    path('', login_required(superuser_required(FullDailyReportListView.as_view())), name='full_dailyreport_list'),
    path('new/',            daily_report,              name='dailyreport'),
    path('success/',        TemplateView.as_view(template_name='reportes/success.html'), name='daily_report_success'),
    path('dailyreports/export/', export_project_reports, name='export_project_reports'),
    path("dailyreports/import/", import_daily_reports, name="import_daily_reports"),
    path('project/<int:project_pk>/reports/', daily_report_list, name='dailyreport_list'),
    path('<int:pk>/',       DailyReportDetailView.as_view(), name='dailyreport_detail'),
    path('<int:pk>/edit/', login_required(superuser_required(DailyReportUpdateView.as_view())), name='dailyreport_edit'),
    path('projects/',          login_required(superuser_required(ProjectListView.as_view())),   name='project_list'),
    path('projects/add/',      login_required(superuser_required(ProjectCreateView.as_view())), name='project_add'),
    path('projects/json/', ProjectListJsonView.as_view(), name='project_list_json'),
    path('projects/<int:pk>/edit/', login_required(superuser_required(ProjectUpdateView.as_view())), name='project_edit'),
    path('projects/<int:pk>/delete/', login_required(superuser_required(ProjectDeleteView.as_view())), name='project_delete'),
    path('clients/<int:pk>/delete/', login_required(superuser_required(client_delete)), name='client_delete'),
    path('clients/add/',           login_required(superuser_required(client_upsert)), name='client_add'),
    path('clients/<int:pk>/edit/', login_required(superuser_required(client_upsert)), name='client_edit'),
    path('clients/',               login_required(superuser_required(client_list)),  name='client_list'),
    path('logout/', logout_view, name='logout'),
    path('api/client-contacts/', client_contacts_json, name='client_contacts_json'),
    
]
