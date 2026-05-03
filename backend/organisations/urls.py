from django.urls import path
from .views import *

urlpatterns = [
    path("create/", CreateOrganisationView.as_view()),
    path("mine/", MyOrganisationsView.as_view()),
    path("<slug:slug>/switch/", SwitchOrganisationView.as_view()),
    path("<slug:slug>/invite/", InviteMemberView.as_view()),
    path("<slug:slug>/members/", OrganisationMembersView.as_view()),
    path("accept/<str:token>/", AcceptInviteView.as_view()),
    path('<slug:slug>/members/<str:username>/', remove_member),
    path('<slug:slug>/members/<str:username>/role/', update_member_role),
    path('<slug:slug>/invites/', list_invites),
    path('<slug:slug>/invites/<str:token>/revoke/', revoke_invite),
]