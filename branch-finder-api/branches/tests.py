import pytest
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from rest_framework.test import APIClient
from branches.models import Branch, DeliveryZone


@pytest.fixture
def sample_data(db):
    """A single square branch zone for predictable testing."""
    branch = Branch.objects.create(
        code="TEST01",
        name="Test Branch",
        location=Point(121.0, 14.5, srid=4326),
    )

    # A simple square polygon covering roughly 120.9-121.1, 14.4-14.6
    square = Polygon((
        (120.9, 14.4), (121.1, 14.4), (121.1, 14.6), (120.9, 14.6), (120.9, 14.4)
    ), srid=4326)

    zone = DeliveryZone.objects.create(
        branch=branch,
        eta_minutes=30,
        geom=MultiPolygon(square, srid=4326),
    )
    return branch, zone


@pytest.mark.django_db
class TestAssignBranchView:
    def test_point_inside_zone_returns_branch(self, sample_data):
        branch, zone = sample_data
        client = APIClient()
        response = client.get("/api/assign/", {"lat": 14.5, "lng": 121.0})

        assert response.status_code == 200
        data = response.json()
        assert data["assigned"] is True
        assert data["branch"]["code"] == "TEST01"
        assert data["eta_minutes"] == 30

    def test_point_outside_zone_returns_not_assigned(self, sample_data):
        client = APIClient()
        response = client.get("/api/assign/", {"lat": 0, "lng": 0})

        assert response.status_code == 200
        data = response.json()
        assert data["assigned"] is False

    def test_missing_params_returns_400(self):
        client = APIClient()
        response = client.get("/api/assign/")

        assert response.status_code == 400

    def test_non_numeric_params_returns_400(self):
        client = APIClient()
        response = client.get("/api/assign/", {"lat": "abc", "lng": "121.0"})

        assert response.status_code == 400

    def test_overlapping_zones_lowest_eta_wins(self, sample_data):
        """Two overlapping zones covering the same point; the 15-min zone should win over 30-min."""
        branch, zone = sample_data

        branch2 = Branch.objects.create(
            code="TEST02",
            name="Test Branch 2",
            location=Point(121.05, 14.55, srid=4326),
        )
        overlapping_square = Polygon((
            (120.95, 14.45), (121.15, 14.45), (121.15, 14.65), (120.95, 14.65), (120.95, 14.45)
        ), srid=4326)
        DeliveryZone.objects.create(
            branch=branch2,
            eta_minutes=15,
            geom=MultiPolygon(overlapping_square, srid=4326),
        )

        client = APIClient()
        response = client.get("/api/assign/", {"lat": 14.5, "lng": 121.0})

        data = response.json()
        assert data["eta_minutes"] == 15
        assert data["branch"]["code"] == "TEST02"


@pytest.mark.django_db
class TestModels:
    def test_branch_str(self, sample_data):
        branch, zone = sample_data
        assert str(branch) == "Test Branch"

    def test_zone_str(self, sample_data):
        branch, zone = sample_data
        assert str(zone) == "Test Branch - 30min"