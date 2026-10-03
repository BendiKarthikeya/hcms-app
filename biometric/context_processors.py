"""
Utility functions related to biometric attendance.

This file contains utility functions related to biometric attendance,
including a function to check if the biometric system is installed.

Functions:
    biometric_is_installed(request): Checks if the biometric system is installed.
"""

from django.core.cache import cache

from base.models import BiometricAttendance


def biometric_is_installed(_request):
    """
    Check if the biometric system is installed.
    Cached for 120 seconds to avoid DB hit on every request.
    """
    cached = cache.get("ctx_biometric_is_installed")
    if cached is not None:
        return cached
    instance = BiometricAttendance.objects.first()
    if not instance:
        BiometricAttendance.objects.create(is_installed=False)
        instance = BiometricAttendance.objects.first()
    is_installed = instance.is_installed
    result = {"is_installed": is_installed}
    cache.set("ctx_biometric_is_installed", result, 120)
    return result
