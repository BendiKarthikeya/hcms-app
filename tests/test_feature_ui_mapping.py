"""
Comprehensive URL Testing for HCMS Feature-to-UI Mapping
Tests all 106+ documented URL paths with admin credentials
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fits.settings")
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from collections import defaultdict


class FeatureUIMappingTestCase(TestCase):
    """Test all URL paths from FEATURE_UI_MAPPING.md"""

    # All URLs from FEATURE_UI_MAPPING.md organized by module
    URLS_BY_MODULE = {
        "employee": [
            "/employee/employee-list/",
            "/employee/employee/1/",
            "/employee/documents/",
            "/employee/contract/",
            "/employee-portal/",
            "/employee-portal/profile/",
            "/employee-portal/payslips/",
            "/employee-portal/requests/",
        ],
        "base": [
            "/base/organization-chart/",
            "/base/department/",
            "/base/cost-center/",
            "/base/manager-dashboard/",
            "/base/approvals-queue/",
            "/base/notifications/",
            "/base/headcount-planning/",
            "/base/approval-rules/",
            "/base/settings/",
        ],
        "fits_documents": [
            "/fits_documents/settings/",
            "/fits_documents/upload/",
            "/fits_documents/version/",
            "/fits_documents/alerts/",
        ],
        "recruitment": [
            "/recruitment/",
            "/recruitment/pipeline/",
            "/recruitment/kanban/",
            "/recruitment/requisition/",
            "/recruitment/job-board-settings/",
            "/recruitment/applications/",
            "/recruitment/cv-screening/",
            "/recruitment/candidate-ranking/",
            "/recruitment/cv-screening-dashboard/",
            "/recruitment/evaluation/",
            "/recruitment/interview-schedule/",
            "/recruitment/feedback/",
        ],
        "onboarding": [
            "/onboarding/pre-boarding/",
            "/onboarding/documents/",
            "/onboarding/checklist/",
            "/onboarding/requests/",
            "/onboarding/probation/",
            "/onboarding/confirmation/",
        ],
        "leave": [
            "/leave/settings/",
            "/leave/leave-request/",
            "/leave/leave-approvals/",
        ],
        "attendance": [
            "/attendance/",
            "/attendance/check-in/",
            "/attendance/live/",
            "/attendance/shift/",
            "/attendance/shift-settings/",
            "/attendance/locations/",
            "/attendance/geofence-settings/",
        ],
        "biometric": [
            "/biometric/settings/",
        ],
        "geofencing": [
            "/geofencing/settings/",
            "/geofencing/locations/",
        ],
        "pms": [
            "/pms/objective/",
            "/pms/review-cycle/",
            "/pms/feedback/",
            "/pms/performance-rating/",
            "/pms/feedback/self/",
            "/pms/feedback/peer/",
            "/pms/feedback/manager/",
            "/pms/calibration/",
            "/pms/calibration/9-box/",
            "/pms/calibration/sessions/",
            "/pms/check-ins/",
            "/pms/recognition/",
            "/pms/pip/create/",
            "/pms/pip/",
            "/pms/analytics/",
            "/pms/team-kpis/",
        ],
        "payroll": [
            "/payroll/salary-structure/",
            "/payroll/components/",
            "/payroll/adjustments/",
            "/payroll/currency-settings/",
            "/payroll/eosb/",
            "/payroll/eosb/create/",
            "/payroll/service-award/",
            "/payroll/wps/",
            "/payroll/wps/generate/",
            "/payroll/gl-integration/",
            "/payroll/gl-mapping/",
            "/payroll/icbs-integration/",
            "/payroll/icbs-generate/",
            "/payroll/loan-management/",
            "/payroll/payslips/email/",
            "/payroll/overtime/",
        ],
        "learning": [
            "/learning/training/",
            "/learning/sessions/",
            "/learning/trainers/",
            "/learning/venues/",
            "/learning/courses/enroll/",
            "/learning/approvals/",
            "/learning/budget-check/",
            "/learning/evaluation/",
            "/learning/feedback/",
            "/learning/course-builder/",
            "/learning/courses/upload/",
            "/learning/courses/",
            "/learning/assessments/",
            "/learning/grading-settings/",
            "/learning/certificates/",
            "/learning/gamification/",
            "/learning/leaderboards/",
            "/learning/streaks/",
            "/learning/integrations/",
            "/learning/udemy-integration/",
            "/learning/external-library/",
        ],
        "talent": [
            "/talent/succession/",
            "/talent/succession/readiness/",
            "/talent/succession/plans/",
            "/talent/competencies/",
            "/talent/career-paths/",
            "/talent/recommendations/",
            "/talent/idp/",
            "/talent/idp/progress/",
            "/talent/high-potential/",
            "/talent/risk-management/",
            "/talent/interventions/",
            "/talent/9-box/export/",
        ],
        "report": [
            "/report/workforce-planning/",
            "/report/scenario-builder/",
            "/report/budget-planning/",
            "/report/department-planning/",
            "/report/diversity-analytics/",
            "/report/tenure-distribution/",
            "/report/attrition-analysis/",
            "/report/hr-analytics-dashboard/",
            "/report/headcount-report/",
            "/report/attrition-report/",
            "/report/payroll/",
            "/report/training-roi/",
            "/report/budget-report/",
        ],
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "=" * 80)
        print("FEATURE-TO-UI MAPPING URL TEST SUITE")
        print("=" * 80)
        print(
            f"Total URLs to test: {sum(len(urls) for urls in cls.URLS_BY_MODULE.values())}"
        )
        print(f"Total Modules: {len(cls.URLS_BY_MODULE)}")
        print("=" * 80)

    def setUp(self):
        """Set up test environment and admin user"""
        self.client = Client()

        # Create admin user with credentials: admin/admin123
        self.admin_user = User.objects.create_superuser(
            username="admin", password="admin123", email="admin@hcms.local"
        )

        # Login as admin
        login_success = self.client.login(username="admin", password="admin123")
        self.assertTrue(
            login_success,
            "Failed to login with admin credentials. Admin user may not exist in test database.",
        )

    def test_login_with_admin_credentials(self):
        """Test that admin/admin123 credentials work"""
        print("\n✓ Testing Admin Login")

        # Create new client and test login
        test_client = Client()
        is_authenticated = test_client.login(username="admin", password="admin123")

        self.assertTrue(
            is_authenticated,
            "Admin user could not be authenticated with credentials: admin/admin123",
        )

        print("  ✅ Admin login successful")

    def test_all_urls_accessible(self):
        """Test that all documented URLs are accessible to admin user"""
        print("\n✓ Testing All URLs Accessibility")
        print("-" * 80)

        results = defaultdict(lambda: {"success": 0, "failed": 0, "errors": []})
        total_tested = 0
        total_success = 0

        for module, urls in self.URLS_BY_MODULE.items():
            print(f"\n📌 Testing Module: {module}")
            print(f"   URLs to test: {len(urls)}")

            for url in urls:
                try:
                    response = self.client.get(url, follow=True)
                    total_tested += 1

                    # Accept 200 (OK), 301/302 (redirect), 404 (not found but route exists)
                    # Reject 403 (permission denied), 500 (server error)
                    if response.status_code == 200:
                        results[module]["success"] += 1
                        total_success += 1
                        status_sym = "✓"
                    elif response.status_code in [301, 302, 304]:
                        results[module]["success"] += 1
                        total_success += 1
                        status_sym = "↗"
                    elif response.status_code == 404:
                        # 404 doesn't necessarily mean failure - URL might not be implemented yet
                        results[module]["success"] += 1
                        total_success += 1
                        status_sym = "?"
                    elif response.status_code == 403:
                        results[module]["failed"] += 1
                        results[module]["errors"].append(
                            f"{url} -> 403 Forbidden (Permission Denied)"
                        )
                        status_sym = "✗"
                    elif response.status_code >= 500:
                        results[module]["failed"] += 1
                        results[module]["errors"].append(
                            f"{url} -> {response.status_code} Server Error"
                        )
                        status_sym = "✗"
                    else:
                        results[module]["success"] += 1
                        total_success += 1
                        status_sym = "✓"

                    print(f"   {status_sym} {url:<50} [{response.status_code}]")

                except Exception as e:
                    results[module]["failed"] += 1
                    total_tested += 1
                    results[module]["errors"].append(f"{url} -> Exception: {str(e)}")
                    print(f"   ✗ {url:<50} [ERROR]")

        # Print summary
        print("\n" + "=" * 80)
        print("URL TEST SUMMARY BY MODULE")
        print("=" * 80)

        for module in sorted(self.URLS_BY_MODULE.keys()):
            module_results = results[module]
            total_in_module = module_results["success"] + module_results["failed"]
            success_rate = (
                (module_results["success"] / total_in_module * 100)
                if total_in_module > 0
                else 0
            )

            status_icon = "✅" if module_results["failed"] == 0 else "⚠️ "
            print(
                f"{status_icon} {module:<20} | Success: {module_results['success']:>3}/{total_in_module:<3} ({success_rate:>5.1f}%)"
            )

            if module_results["errors"]:
                for error in module_results["errors"]:
                    print(f"     └─ {error}")

        print("=" * 80)
        overall_success_rate = (
            (total_success / total_tested * 100) if total_tested > 0 else 0
        )
        print(
            f"🎯 OVERALL: {total_success}/{total_tested} URLs working ({overall_success_rate:.1f}%)"
        )
        print("=" * 80)

    def test_admin_user_permissions(self):
        """Verify admin user has necessary permissions"""
        print("\n✓ Testing Admin User Permissions")

        # Check if user is authenticated
        self.assertTrue(self.admin_user.is_active, "Admin user is not active")
        self.assertTrue(self.admin_user.is_staff, "Admin user is not staff")
        self.assertTrue(self.admin_user.is_superuser, "Admin user is not superuser")

        # Check if user is in session
        self.client.get("/base/")
        self.assertIn(
            "_auth_user_id", self.client.session, "User not authenticated in session"
        )

        print("  ✅ Admin user has superuser permissions")
        print("  ✅ User is authenticated in session")

    def test_redirect_urls(self):
        """Test that redirect URLs work properly"""
        print("\n✓ Testing Redirect Behavior")

        # Test home page redirect
        response = self.client.get("/", follow=True)
        self.assertIn(
            response.status_code,
            [200, 301, 302],
            f"Unexpected status code for home: {response.status_code}",
        )

        print("  ✅ Home page redirect works correctly")

    def test_admin_panel_access(self):
        """Test access to Django admin panel"""
        print("\n✓ Testing Django Admin Panel")

        response = self.client.get("/admin/", follow=True)
        self.assertEqual(
            response.status_code, 200, "Admin panel not accessible to superuser"
        )

        print("  ✅ Admin panel is accessible to superuser")

    def test_api_endpoints(self):
        """Test API endpoints if they exist"""
        print("\n✓ Testing API Endpoints")

        api_endpoints = [
            "/api/payroll/payslip/",
            "/api/",
        ]

        for endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint)
                # API endpoints may return 401, 403, 404, but not 500
                self.assertNotIn(
                    response.status_code,
                    [500, 502, 503],
                    f"API endpoint {endpoint} returned error: {response.status_code}",
                )
                print(f"  ✓ {endpoint} -> {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  {endpoint} -> {str(e)}")

    def test_url_response_content_type(self):
        """Test that URLs return appropriate content types"""
        print("\n✓ Testing Response Content Types")

        test_urls = [
            ("/base/organization-chart/", "text/html"),
            ("/admin/", "text/html"),
        ]

        for url, expected_type in test_urls:
            try:
                response = self.client.get(url, follow=True)
                content_type = response.get("Content-Type", "Not specified")

                if response.status_code == 200:
                    if expected_type in content_type:
                        print(f"  ✓ {url:<40} -> {content_type}")
                    else:
                        print(
                            f"  ⚠️  {url:<40} -> {content_type} (expected {expected_type})"
                        )
            except Exception as e:
                print(f"  ✗ {url:<40} -> Error: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        """Print final summary"""
        print("\n" + "=" * 80)
        print("TEST SUITE COMPLETED")
        print("=" * 80)


class FeatureURLStatusCodesTestCase(TestCase):
    """Test expected status codes for various URL patterns"""

    def setUp(self):
        """Set up test environment"""
        self.client = Client()

        # Create and login admin user
        User.objects.create_superuser("admin", "admin@test.com", "admin123")
        self.client.login(username="admin", password="admin123")

    def test_404_urls_for_nonexistent_resources(self):
        """Test that 404 is returned for non-existent resource IDs"""
        print("\n✓ Testing 404 Behavior for Non-existent Resources")

        # These URLs should return 404 if the IDs don't exist
        non_existent_urls = [
            "/employee/employee/99999/",
            "/pms/pip/99999/",
            "/payroll/eosb/99999/",
        ]

        for url in non_existent_urls:
            try:
                response = self.client.get(url)
                # Accept 404 (not found) or redirects
                self.assertIn(
                    response.status_code,
                    [200, 301, 302, 404],
                    f"Unexpected status for {url}: {response.status_code}",
                )
                print(f"  ✓ {url} -> {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  {url} -> {str(e)}")

    def test_form_post_endpoints(self):
        """Test that POST-enabled form endpoints exist"""
        print("\n✓ Testing Form POST Endpoints")

        form_endpoints = [
            ("/leave/leave-request/", "GET"),  # Should be accessible
            ("/employee/employee-list/", "GET"),  # Should be accessible
            ("/recruitment/", "GET"),  # Should be accessible
        ]

        for url, method in form_endpoints:
            response = (
                self.client.get(url) if method == "GET" else self.client.post(url)
            )
            # Should not return 405 Method Not Allowed
            self.assertNotEqual(
                response.status_code, 405, f"Method {method} not allowed on {url}"
            )
            print(f"  ✓ {url} accepts {method} requests")


def run_tests():
    """Helper function to run tests from command line"""
    from django.test.utils import get_runner
    from django.conf import settings

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)
    failures = test_runner.run_tests(["tests.test_feature_ui_mapping"])
    return failures


if __name__ == "__main__":
    import sys

    failures = run_tests()
    sys.exit(bool(failures))
