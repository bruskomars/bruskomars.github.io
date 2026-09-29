from django.urls import path
from .views import BranchListView, DeliveryZoneListView, AssignBranchView

urlpatterns = [
    path("branches/", BranchListView.as_view(), name="branch-list"),
    path("zones/", DeliveryZoneListView.as_view(), name="zone-list"),
    path("assign/", AssignBranchView.as_view(), name="assign-branch"),
]