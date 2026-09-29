import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.db import transaction
from branches.models import Branch, DeliveryZone

BRANCH_FILE, ZONE_FILE = "data/branches.geojson", "data/rta.geojson"
BRANCH_CODE, BRANCH_NAME = "RTA_ID", "BRANCH"
ZONE_BRANCH, ZONE_ETA = "RTA_ID", "TIME"


def geom_from(feature):
    g = GEOSGeometry(json.dumps(feature["geometry"]), srid=4326)
    if not g.valid:
        g = g.buffer(0)  # repair simple invalid geometries
    return g


class Command(BaseCommand):
    help = "Load branches and delivery zones from GeoJSON"

    @transaction.atomic
    def handle(self, *args, **opts):
        DeliveryZone.objects.all().delete()
        Branch.objects.all().delete()

        with open(BRANCH_FILE) as f:
            branches = {}
            for ft in json.load(f)["features"]:
                p = ft["properties"]
                b = Branch.objects.create(
                    code=str(p[BRANCH_CODE]), name=p[BRANCH_NAME], location=geom_from(ft)
                )
                branches[b.code] = b

        zones, skipped = [], 0
        with open(ZONE_FILE) as f:
            for ft in json.load(f)["features"]:
                p = ft["properties"]
                b = branches.get(str(p[ZONE_BRANCH]))
                if b is None:
                    skipped += 1
                    continue
                g = geom_from(ft)
                if g.geom_type == "Polygon":
                    g = MultiPolygon(g, srid=4326)
                zones.append(DeliveryZone(branch=b, eta_minutes=int(p[ZONE_ETA]), geom=g))
        DeliveryZone.objects.bulk_create(zones)

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(branches)} branches, {len(zones)} zones ({skipped} skipped, no matching branch)"
        ))