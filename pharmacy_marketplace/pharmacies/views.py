"""
Pharmacies app views — pharmacy CRUD, storefront detail, and location updates.

Pharmacy owners manage their own storefronts via JWT-authenticated endpoints.
Public pharmacy detail views require no authentication.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from pharmacies.models import Pharmacy
from pharmacies.serializers import (
    PharmacyDetailSerializer,
    PharmacyLocationSerializer,
    PharmacyRegistrationSerializer,
    PharmacyUpdateSerializer,
)


def _get_owner_pharmacy(user):
    """Return the first pharmacy owned by the given user, or ``None``."""
    if user.is_authenticated and hasattr(user, "pharmacies"):
        return user.pharmacies.first()
    return None


class IsPharmacyOwner(permissions.BasePermission):
    """Grant access only to users with role=pharmacy_owner."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "pharmacy_owner"
        )


class IsOwnerOfPharmacy(permissions.BasePermission):
    """Grant access only if the pharmacy's owner matches the request user."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


# ── Create ──────────────────────────────────────────────────────────────────────


class PharmacyCreateView(generics.CreateAPIView):
    """Create a new pharmacy for the authenticated owner.

    POST /api/v1/pharmacies/
    Automatically sets ``owner`` to the request user.
    Accepts location as a GeoJSON Point::

        {"location": {"type": "Point", "coordinates": [90.4125, 23.8103]}}
    """

    queryset = Pharmacy.objects.all()
    serializer_class = PharmacyRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsPharmacyOwner]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ── Retrieve + Update (Public detail / Owner edit) ─────────────────────────────


class PharmacyRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """Public pharmacy storefront detail + owner profile updates.

    GET  /api/v1/pharmacies/{id}/  — public, no auth
    PATCH /api/v1/pharmacies/{id}/ — owner-only, accepts partial updates
    """

    queryset = Pharmacy.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PharmacyDetailSerializer
        return PharmacyUpdateSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsPharmacyOwner(), IsOwnerOfPharmacy()]


# ── Location Update ─────────────────────────────────────────────────────────────


class PharmacyLocationUpdateView(generics.UpdateAPIView):
    """Update only the pharmacy's geolocation pin.

    PATCH /api/v1/pharmacies/{id}/location/
    Owner-only. Accepts ``{location: {type: "Point", coordinates: [lng, lat]}}``.
    """

    queryset = Pharmacy.objects.all()
    serializer_class = PharmacyLocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsPharmacyOwner, IsOwnerOfPharmacy]


# ── Deactivate (Owner) ──────────────────────────────────────────────────────────


class PharmacyDeactivateView(generics.UpdateAPIView):
    """Temporarily suspend a pharmacy's storefront visibility.

    PATCH /api/v1/pharmacies/{id}/deactivate/
    Owner-only. Sets ``status`` to ``suspended``.
    """

    queryset = Pharmacy.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPharmacyOwner, IsOwnerOfPharmacy]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = Pharmacy.Status.SUSPENDED
        instance.save(update_fields=["status"])
        return Response(
            {"message": _("Pharmacy has been deactivated."), "status": instance.status},
            status=status.HTTP_200_OK,
        )
