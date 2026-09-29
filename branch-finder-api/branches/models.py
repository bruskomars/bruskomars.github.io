from django.contrib.gis.db import models


class Branch(models.Model):
    code = models.CharField(max_length=50, unique=True)  # ID from your source data
    name = models.CharField(max_length=150)
    location = models.PointField(srid=4326)

    def __str__(self):
        return self.name


class DeliveryZone(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="zones")
    eta_minutes = models.PositiveSmallIntegerField()
    geom = models.MultiPolygonField(srid=4326)  # GiST index is created automatically

    class Meta:
        indexes = [models.Index(fields=["eta_minutes"])]

    def __str__(self):
        return f"{self.branch.name} - {self.eta_minutes}min"