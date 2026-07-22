"""
Web (session-based) authentication views for customer and owner surfaces.

These views handle registration, login, and OTP verification for the
Django-template-based web frontend. They use Django session auth (not JWT),
which is reserved for the API consumed by non-session clients (Flutter).
"""

import json
import logging

from django.contrib import messages as django_messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from accounts.models import User

logger = logging.getLogger(__name__)


class CustomerRegistrationView(TemplateView):
    """Customer registration — single step form.

    GET  /customer/register/  → renders registration form
    POST /customer/register/  → creates user, logs in, returns OTP partial (htmx)
    """

    template_name = "customer/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["already_logged_in"] = True
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")

        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        errors = {}

        # Validate
        if not full_name:
            errors["full_name"] = _("Please enter your full name.")
        if not phone:
            errors["phone"] = _("Please enter your phone number.")
        elif not phone.startswith("01") or len(phone) != 11 or not phone.isdigit():
            errors["phone"] = _(
                "Please enter a valid Bangladeshi phone number (e.g., 01XXXXXXXXX)."
            )
        elif User.objects.filter(phone=phone).exists():
            errors["phone"] = _("This phone number is already registered. Sign in instead.")

        if not password:
            errors["password"] = _("Please enter a password.")
        elif len(password) < 8:
            errors["password"] = _("Password must be at least 8 characters.")

        if password != confirm_password:
            errors["confirm_password"] = _("Passwords do not match.")

        if errors:
            return render(request, self.template_name, {
                "errors": errors,
                "values": request.POST,
            })

        # Create user
        user = User.objects.create_user(
            phone=phone,
            full_name=full_name,
            password=password,
            role="customer",
        )

        # Log in via session auth
        django_login(request, user)

        # Return OTP verification partial (htmx swap)
        return render(request, "partials/_otp_verify.html", {
            "phone": phone,
            "redirect_url": "/",
            "error_url": reverse("auth:customer-register"),
        })


class CustomerLoginView(TemplateView):
    """Customer login — phone + password form.

    GET  /customer/login/  → renders login form
    POST /customer/login/  → authenticates and redirects
    """

    template_name = "customer/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["already_logged_in"] = True
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")

        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        errors = {}

        if not phone:
            errors["phone"] = _("Please enter your phone number.")
        if not password:
            errors["password"] = _("Please enter your password.")

        if not errors:
            user = authenticate(request, username=phone, password=password)
            if user is None:
                # Generic error — don't reveal which field is wrong
                errors["general"] = _("Invalid phone number or password. Please try again.")
            elif not user.is_active:
                errors["general"] = _("This account is no longer active. Please contact support.")
            else:
                django_login(request, user)
                # Update header via htmx or full redirect
                next_url = request.GET.get("next", "/")
                if request.htmx:
                    response = HttpResponse()
                    response["HX-Redirect"] = next_url
                    return response
                return redirect(next_url)

        return render(request, self.template_name, {
            "errors": errors,
            "values": request.POST,
        })


class OwnerRegistrationView(TemplateView):
    """Pharmacy owner registration — multi-step form.

    GET  /owner/register/  → renders step 1
    POST /owner/register/  → processes current step via htmx
    """

    template_name = "owner/register.html"
    STEP_LABELS = ["Account", "Pharmacy", "Location", "Review"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("owner:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Reset session data on fresh GET
        if "owner_registration" in request.session:
            del request.session["owner_registration"]
        return render(request, self.template_name, {
            "step": 0,
            "step_labels": self.STEP_LABELS,
        })

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get("step", 0))

        # Load existing session data
        data = request.session.get("owner_registration", {})

        if step == 0:
            # Step 1: Account info
            full_name = request.POST.get("full_name", "").strip()
            phone = request.POST.get("phone", "").strip()
            password = request.POST.get("password", "")
            confirm_password = request.POST.get("confirm_password", "")

            errors = {}
            if not full_name:
                errors["full_name"] = _("Please enter your full name.")
            if not phone:
                errors["phone"] = _("Please enter your phone number.")
            elif not phone.startswith("01") or len(phone) != 11 or not phone.isdigit():
                errors["phone"] = _(
                    "Please enter a valid Bangladeshi phone number (e.g., 01XXXXXXXXX)."
                )
            elif User.objects.filter(phone=phone).exists():
                errors["phone"] = _("This phone number is already registered.")
            if not password:
                errors["password"] = _("Please enter a password.")
            elif len(password) < 8:
                errors["password"] = _("Password must be at least 8 characters.")
            if password != confirm_password:
                errors["confirm_password"] = _("Passwords do not match.")

            if errors:
                return render(request, self.template_name, {
                    "step": 0,
                    "step_labels": self.STEP_LABELS,
                    "errors": errors,
                    "values": request.POST,
                })

            data.update({
                "full_name": full_name,
                "phone": phone,
                "password": password,  # stored temporarily in session
            })
            request.session["owner_registration"] = data
            return render(request, self.template_name, {
                "step": 1,
                "step_labels": self.STEP_LABELS,
                "values": data,
            })

        elif step == 1:
            # Step 2: Pharmacy details
            pharm_name = request.POST.get("pharmacy_name", "").strip()
            address = request.POST.get("address_line", "").strip()
            city = request.POST.get("city", "").strip()
            division = request.POST.get("division", "").strip()
            pharm_phone = request.POST.get("pharmacy_phone", "").strip()
            dgda_license = request.POST.get("dgda_license_number", "").strip()
            pharmacist_name = request.POST.get("pharmacist_name", "").strip()
            pharmacist_reg = request.POST.get("pharmacist_reg_number", "").strip()
            operating_hours_raw = request.POST.get("operating_hours", "{}")

            errors = {}
            if not pharm_name:
                errors["pharmacy_name"] = _("Please enter your pharmacy name.")
            if not address or len(address) < 10:
                errors["address_line"] = _("Please enter a full address (at least 10 characters).")
            if not city:
                errors["city"] = _("Please select a city.")
            if not division:
                errors["division"] = _("Please select a division.")
            if not pharm_phone:
                errors["pharmacy_phone"] = _("Please enter a pharmacy phone number.")

            if errors:
                return render(request, self.template_name, {
                    "step": 1,
                    "step_labels": self.STEP_LABELS,
                    "errors": errors,
                    "values": request.POST,
                    "data": data,
                })

            # Parse operating hours
            try:
                operating_hours = json.loads(operating_hours_raw) if operating_hours_raw else {}
            except (json.JSONDecodeError, TypeError):
                operating_hours = {}

            data.update({
                "pharmacy_name": pharm_name,
                "address_line": address,
                "city": city,
                "division": division,
                "pharmacy_phone": pharm_phone,
                "dgda_license_number": dgda_license or None,
                "pharmacist_name": pharmacist_name or None,
                "pharmacist_reg_number": pharmacist_reg or None,
                "operating_hours": operating_hours,
            })
            request.session["owner_registration"] = data
            return render(request, self.template_name, {
                "step": 2,
                "step_labels": self.STEP_LABELS,
                "values": data,
            })

        elif step == 2:
            # Step 3: Location
            lat = request.POST.get("location_latitude", request.POST.get("loc_latitude", ""))
            lng = request.POST.get("location_longitude", request.POST.get("loc_longitude", ""))

            errors = {}
            if not lat or not lng:
                errors["location"] = _(
                    "Please place a pin on the map to set your pharmacy location."
                )

            if errors:
                return render(request, self.template_name, {
                    "step": 2,
                    "step_labels": self.STEP_LABELS,
                    "errors": errors,
                    "data": data,
                })

            try:
                data["latitude"] = float(lat)
                data["longitude"] = float(lng)
            except (ValueError, TypeError):
                errors["location"] = _("Invalid coordinates. Please place the pin on the map.")
                return render(request, self.template_name, {
                    "step": 2,
                    "step_labels": self.STEP_LABELS,
                    "errors": errors,
                    "data": data,
                })

            request.session["owner_registration"] = data
            return render(request, self.template_name, {
                "step": 3,
                "step_labels": self.STEP_LABELS,
                "values": data,
            })

        elif step == 3:
            # Step 4: Review & Submit
            return self._complete_registration(request, data)

        return render(request, self.template_name, {
            "step": 0,
            "step_labels": self.STEP_LABELS,
        })

    def _complete_registration(self, request, data):
        """Create user + pharmacy, log in, return OTP verification partial."""
        try:
            try:
                from pharmacies.models import Pharmacy
            except Exception:
                Pharmacy = None  # noqa: N806 — intentional fallback for optional import

            # Create user
            user = User.objects.create_user(
                phone=data["phone"],
                full_name=data["full_name"],
                password=data["password"],
                role="pharmacy_owner",
            )

            # Create pharmacy
            if Pharmacy is not None:
                try:
                    from django.contrib.gis.geos import Point
                    location = Point(data["longitude"], data["latitude"], srid=4326)
                except ImportError:
                    location = None

                if location is not None:
                    Pharmacy.objects.create(
                        owner=user,
                        name=data["pharmacy_name"],
                        address_line=data["address_line"],
                        city=data["city"],
                        division=data["division"],
                        location=location,
                        phone=data["pharmacy_phone"],
                        dgda_license_number=data.get("dgda_license_number"),
                        pharmacist_name=data.get("pharmacist_name"),
                        pharmacist_registration_number=data.get("pharmacist_reg_number"),
                        operating_hours=data.get("operating_hours", {}),
                    )
                else:
                    # Create pharmacy without GIS location (fallback for testing)
                    Pharmacy.objects.create(
                        owner=user,
                        name=data["pharmacy_name"],
                        address_line=data["address_line"],
                        city=data["city"],
                        division=data["division"],
                        phone=data["pharmacy_phone"],
                        dgda_license_number=data.get("dgda_license_number"),
                        pharmacist_name=data.get("pharmacist_name"),
                        pharmacist_registration_number=data.get("pharmacist_reg_number"),
                        operating_hours=data.get("operating_hours", {}),
                    )

            # Log in
            django_login(request, user)

            # Clear session data
            del request.session["owner_registration"]

            # Return OTP verification partial for htmx swap
            return render(request, "partials/_otp_verify.html", {
                "phone": data["phone"],
                "redirect_url": reverse("owner:dashboard"),
                "error_url": reverse("auth:owner-register"),
            })

        except Exception:
            logger.exception("Owner registration failed")
            return render(request, self.template_name, {
                "step": 3,
                "step_labels": self.STEP_LABELS,
                "error": _("Something went wrong on our end. Please try again."),
                "values": data,
            })


class OwnerLoginView(TemplateView):
    """Pharmacy owner login — phone + password form.

    GET  /owner/login/  → renders owner login form
    POST /owner/login/  → authenticates and redirects to dashboard
    """

    template_name = "owner/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("owner:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        errors = {}

        if not phone:
            errors["phone"] = _("Please enter your phone number.")
        if not password:
            errors["password"] = _("Please enter your password.")

        if not errors:
            user = authenticate(request, username=phone, password=password)
            if user is None:
                errors["general"] = _("Invalid phone number or password. Please try again.")
            elif not user.is_active:
                errors["general"] = _("This account is no longer active. Please contact support.")
            elif user.role != "pharmacy_owner":
                errors["general"] = _("This account is not registered as a pharmacy owner.")
            else:
                django_login(request, user)
                # Check if pharmacy exists
                try:
                    from pharmacies.models import Pharmacy
                except Exception:
                    Pharmacy = None  # noqa: N806 — intentional fallback for optional import
                if Pharmacy and not Pharmacy.objects.filter(owner=user, status="active").exists():
                    pass  # active pharmacy check (available for future use)
                if request.htmx:
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse("owner:dashboard")
                    return response
                return redirect("owner:dashboard")

        return render(request, self.template_name, {
            "errors": errors,
            "values": request.POST,
        })


class OwnerDashboardView(LoginRequiredMixin, TemplateView):
    """Pharmacy owner dashboard shell.

    GET /owner/dashboard/  → renders dashboard with pharmacy data
    """

    template_name = "owner/dashboard.html"
    login_url = "/owner/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            from pharmacies.models import Pharmacy
        except Exception:
            Pharmacy = None  # noqa: N806 — intentional fallback for optional import
        pharmacy = Pharmacy.objects.filter(owner=user).first() if Pharmacy else None

        context["user"] = user
        context["pharmacy"] = pharmacy
        context["has_pharmacy"] = pharmacy is not None

        if pharmacy:
            context["pharmacy_status_display"] = {
                "active": "Active",
                "suspended": "Suspended",
                "pending_review": "Pending Review",
            }.get(pharmacy.status, pharmacy.status)

            context["pharmacy_status_badge"] = {
                "active": "badge-success",
                "suspended": "badge-danger",
                "pending_review": "badge-warning",
            }.get(pharmacy.status, "badge-info")

            # Determine first-login state.
            # The custom User model extends AbstractBaseUser (no date_joined field),
            # so we detect first login by checking last_login is None.
            context["is_first_login"] = user.last_login is None

        return context


@require_POST
def logout_view(request):
    """Log out the user and redirect based on role."""
    role = getattr(request.user, "role", None)
    django_logout(request)

    if role == "pharmacy_owner":
        django_messages.info(request, _("You've been logged out."))
        return redirect("/owner/login/")
    return redirect("/")


def customer_register_redirect(request):
    return redirect("auth:customer-register")


def owner_register_redirect(request):
    return redirect("auth:owner-register")
