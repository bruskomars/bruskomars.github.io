from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Branch, DeliveryZone


class BranchSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Branch
        geo_field = "location"
        fields = ["id", "code", "name"]


class DeliveryZoneSerializer(GeoFeatureModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = DeliveryZone
        geo_field = "geom"
        fields = ["id", "branch", "branch_name", "eta_minutes"]