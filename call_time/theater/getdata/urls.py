from . import views
from django.urls import path, re_path
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'getdata'

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('venues/', views.VenueView.as_view(), name='venues'),
    path('user/login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('documents/', views.UploadsView.as_view(), name='documents'),
    # /info/23/
    re_path(r'^info/(?P<pk>[0-9]+)/$', views.InfoView.as_view(), name='info'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('privacy/', views.PrivacyChange.as_view(), name='privacy'),
    path('email-notice/', views.EmailNoticeChange.as_view(), name='email-notice'),
    path('alert/', views.SendAlert.as_view(), name='alert'),
    path('user/register/', views.UserFormView.as_view(), name='register'),
    path('user/registercompany/', views.CompanyFormView.as_view(), name='registercompany'),
    path('performer/add/', views.AddPerformer.as_view(), name='add-performer'),
    path('show/add/', views.ShowCreate.as_view(), name='show-add'),
    path('role/add/', views.RoleCreate.as_view(), name='role-add'),
    path('call/add/', views.CallCreate.as_view(), name='call-add'),
    path('quick/add/', views.QuickCreate.as_view(), name='quick-add'),
    path('venue/add/', views.VenueCreate.as_view(), name='venue-add'),
    path('documents/add/', views.UploadsCreate.as_view(), name='documents-add'),
    path('schedule/', views.CreatePDF.as_view(), name='schedule'),
    path('schedule-view/', views.ViewPDF.as_view(), name='schedule-view'),
    path('staff/add/', views.AddStaff.as_view(), name='staff-add'),
    path('staffinfo/', views.StaffView.as_view(), name='staffinfo'),
    re_path(r'^showinfo/(?P<pk>[0-9]+)/$', views.ShowInfoView.as_view(), name='showinfo'),
    re_path(r'^roleinfo/(?P<pk>[0-9]+)/$', views.RoleInfoView.as_view(), name='roleinfo'),
    re_path(r'^callinfo/(?P<pk>[0-9]+)/$', views.CallInfoView.as_view(), name='callinfo'),
    re_path(r'^venueinfo/(?P<pk>[0-9]+)/$', views.VenueInfoView.as_view(), name='venueinfo'),
    re_path(r'^venue/(?P<pk>[0-9]+)/$', views.VenueUpdate.as_view(), name='venue-update'),
    re_path(r'^venue/(?P<pk>[0-9]+)/delete/$', views.VenueDelete.as_view(), name='venue-delete'),
    re_path(r'^quick/(?P<pk>[0-9]+)/$', views.QuickUpdate.as_view(), name='quick-update'),
    re_path(r'^quick/(?P<pk>[0-9]+)/delete/$', views.QuickDelete.as_view(), name='quick-delete'),
    re_path(r'^call/(?P<pk>[0-9]+)/$', views.CallUpdate.as_view(), name='call-update'),
    re_path(r'^call/(?P<pk>[0-9]+)/delete/$', views.CallDelete.as_view(), name='call-delete'),
    re_path(r'^performer/(?P<pk>[0-9]+)/$', views.PerformerUpdate.as_view(), name='performer-update'),
    # re_path(r'^performer/(?P<pk>[0-9]+)/delete/$', views.PerformerDelete.as_view(), name='performer-delete'),
    re_path(r'^documents/(?P<pk>[0-9]+)/$', views.UploadsUpdate.as_view(), name='documents-update'),
    re_path(r'^documents/(?P<pk>[0-9]+)/delete/$', views.UploadsDelete.as_view(), name='documents-delete'),
    re_path(r'^show/(?P<pk>[0-9]+)/$', views.ShowUpdate.as_view(), name='show-update'),
    re_path(r'^show/(?P<pk>[0-9]+)/delete/$', views.ShowDelete.as_view(), name='show-delete'),
    re_path(r'^role/(?P<pk>[0-9]+)/$', views.RoleUpdate.as_view(), name='role-update'),
    re_path(r'^role/(?P<pk>[0-9]+)/delete/$', views.RoleDelete.as_view(), name='role-delete'),
    re_path(r'^company/(?P<pk>[0-9]+)/$', views.CompanyUpdate.as_view(), name='company-update'),
    re_path(r'^company/(?P<pk>[0-9]+)/performers$', views.CompanyPerformersUpdate.as_view(), name='companyperformers-update'),
    re_path(r'^staff/(?P<pk>[0-9]+)/$', views.StaffUpdate.as_view(), name='staff-update'),
    re_path(r'^staff/(?P<pk>[0-9]+)/delete/$', views.StaffDelete.as_view(), name='staff-delete'),
    re_path(r'^artists/(?P<pk>[0-9]+)/$', views.ArtistsView.as_view(), name='artists'),
    re_path(r'^artists/(?P<pk>[0-9]+)/delete/$', views.CompanyPerformersDeleteAll.as_view(), name='artists-delete-all'),
    path('addme/', views.AddLink.as_view(), name='addme'),
    re_path(r'^categoryinfo/(?P<pk>[0-9]+)/$', views.CategoryInfo.as_view(), name='categoryinfo'),
    path('category/add/', views.CategoryCreate.as_view(), name='category-add'),
    re_path(r'^category/(?P<pk>[0-9]+)/$', views.CategoryUpdate.as_view(), name='category-update'),
    re_path(r'^category/(?P<pk>[0-9]+)/delete/$', views.CategoryDelete.as_view(), name='category-delete'),
    re_path(r'^user/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='user-update'),
    re_path(r'^logo/(?P<pk>[0-9]+)/$', views.LogoUpdate.as_view(), name='logo'),
    path('conflict/add/', views.ConflictCreate.as_view(), name='conflict-add'),
    re_path(r'^conflict/(?P<pk>[0-9]+)/$', views.ConflictUpdate.as_view(), name='conflict-update'),
    re_path(r'^conflict/(?P<pk>[0-9]+)/delete/$', views.ConflictDelete.as_view(), name='conflict-delete'),
    re_path(r'^conflictinfo/(?P<pk>[0-9]+)/$', views.ConflictInfo.as_view(), name='conflictinfo'),
    path('conflicts/', views.ConflictView.as_view(), name='conflicts'),
    path(r'^join/$', views.JoinChange.as_view(), name='join'),
    path('feedback/', views.Feedback.as_view(), name='feedback'),

]