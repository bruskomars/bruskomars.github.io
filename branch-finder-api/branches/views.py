from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import Branch, DeliveryZone
from .serializers import BranchSerializer, DeliveryZoneSerializer


class BranchListView(ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class DeliveryZoneListView(ListAPIView):
    queryset = DeliveryZone.objects.select_related("branch").all()
    serializer_class = DeliveryZoneSerializer


class AssignBranchView(APIView):
    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if lat is None or lng is None:
            return Response({"error": "lat and lng query params are required"}, status=400)

        try:
            lat, lng = float(lat), float(lng)
        except ValueError:
            return Response({"error": "lat and lng must be numbers"}, status=400)

        pt = Point(lng, lat, srid=4326)  # PostGIS order: lng, lat

        zone = (
            DeliveryZone.objects
            .filter(geom__contains=pt)
            .annotate(distance=Distance("branch__location", pt))
            .order_by("eta_minutes", "distance")
            .select_related("branch")
            .first()
        )

        if zone is None:
            return Response({"assigned": False, "message": "No coverage at this location"}, status=200)

        return Response({
            "assigned": True,
            "branch": {
                "code": zone.branch.code,
                "name": zone.branch.name,
            },
            "eta_minutes": zone.eta_minutes,
        })
