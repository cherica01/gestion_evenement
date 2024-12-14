from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.custom_login, name='login'),
    path('participants/', views.participant_dashboard, name='participant_dashboard'),
    path('organisateurs/', views.organisateur_dashboard, name='organisateur_dashboard'),
    path('creer_evenement/', views.creer_evenement, name='creer_evenement'),
    path('modifier_evenement/<int:id>/', views.modifier_evenement, name='modifier_evenement'),
    path('supprimer_evenement/<int:id>/', views.supprimer_evenement, name='supprimer_evenement'),
    path('inscrire/<int:id>/', views.inscrire_evenement, name='inscrire_evenement'),
    path('desinscrire/<int:id>/', views.desinscrire_evenement, name='desinscrire_evenement'),
    path('participants_evenement/<int:id>/', views.participants_evenement, name='participants_evenement'),
    path('evenement/<int:evenement_id>/envoyer-notification/', views.envoyer_notification, name='envoyer_notification'),
    path('evenement/details/<int:id>/', views.evenement_details, name='evenement_details'),
    path('logout/', views.custom_login, name='logout'),

]
