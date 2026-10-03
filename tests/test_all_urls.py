#!/usr/bin/env python
"""
Comprehensive URL Testing Script for HCMS
Tests all 106 documented URLs and reports status
"""

import os
import sys
import django
import time
from collections import defaultdict

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
sys.path.insert(0, "/Users/karthikeya/Downloads/Omen-2/hcms")

django.setup()

from django.test import Client

# All URLs to test from the dashboard
URLS_TO_TEST = {
    "PIP": [
        "/pms/pip-list/",
        "/pms/pip-create/",
        "/pms/pip/1/",
        "/pms/pip-update/1/",
        "/pms/pip-approve/1/",
        "/pms/pip-review/1/",
        "/pms/pip-extension/1/",
        "/pms/pip-complete/1/",
        "/pms/pip-templates/",
        "/pms/pip-template-create/",
        "/pms/pip-template-update/1/",
        "/pms/pip-dashboard/",
    ],
    "EOSB": [
        "/payroll/eosb-list/",
        "/payroll/eosb-create/",
        "/payroll/eosb/1/",
        "/payroll/eosb-export/",
        "/payroll/eosb-approve/1/",
        "/payroll/eosb-director-approve/1/",
        "/payroll/eosb-mark-paid/1/",
        "/payroll/eosb-bulk-calculate/",
        "/payroll/eosb-dashboard/",
        "/payroll/eosb-settings/",
    ],
    "WPS": [
        "/payroll/wps-file-list/",
        "/payroll/wps-file-generate/",
        "/payroll/wps-file/1/",
        "/payroll/wps-file-approve/1/",
        "/payroll/wps-file-submit/1/",
        "/payroll/wps-file-download/1/",
        "/payroll/wps-file-process-response/1/",
        "/payroll/wps-file-resubmit/1/",
        "/payroll/wps-exceptions/",
        "/payroll/wps-exception-resolve/1/",
        "/payroll/wps-global-settings/",
        "/payroll/wps-dashboard/",
    ],
    "Employee": [
        "/employee/employee-list/",
        "/employee/employee/1/view/",
        "/employee/employee-create/",
        "/employee/employee-update/1/",
        "/employee/user-dashboard/",
        "/employee/contract/",
        "/employee/promotion/",
        "/employee/resignation/",
        "/employee/user-settings/",
        "/employee/document/",
        "/employee/shift-request/",
        "/employee/bank-details/",
        "/employee/employment-letter-generate/",
        "/employee/salary-revision/",
        "/organization/organization-chart/",
    ],
    "Recruitment": [
        "/recruitment/",
        "/recruitment/recruitment-list/",
        "/recruitment/candidate-list/",
        "/recruitment/job-create/",
        "/recruitment/candidate-create/",
        "/recruitment/interview-schedule/",
        "/recruitment/offer-letter/",
        "/recruitment/offer-letter-list/",
        "/recruitment/offer-letter-create/",
        "/recruitment/job-details/1/",
    ],
    "Onboarding": [
        "/onboarding/",
        "/onboarding/candidate-list/",
        "/onboarding/onboarding-stage/",
        "/onboarding/onboarding-task/",
    ],
    "Performance": [
        "/pms/performance-rating/",
        "/pms/performance-rating/create/",
        "/pms/objective-list-view/",
        "/pms/objective-creation/",
        "/pms/feedback-view/",
        "/pms/feedback-creation/",
        "/pms/meeting-list/",
        "/pms/meeting-create/",
        "/pms/bonus-point-setting/",
        "/pms/appraisal-list/",
        "/pms/employee-objective/",
        "/pms/question-template-creation/",
        "/pms/period-create/",
        "/pms/dashboard-view/",
        "/pms/talent-calibration/",
        "/pms/talent-calibration-create/",
        "/pms/calibration-sessions/",
        "/pms/competitor-benchmark/",
    ],
    "Payroll": [
        "/payroll/contract/",
        "/payroll/contract-create/",
        "/payroll/payslip/",
        "/payroll/payslip-create/",
        "/payroll/payroll-generator/",
        "/payroll/salary-component/",
        "/payroll/payroll-tax/",
        "/payroll/payroll-deduction/",
        "/payroll/payroll-settings/",
        "/payroll/auto-payslip/",
        "/payroll/reimbursement/",
        "/payroll/expense-claim/",
        "/payroll/asset-request/",
        "/payroll/loan-request/",
        "/payroll/loan-process/",
        "/payroll/gratuity-pension/",
        "/payroll/leave-encashment/",
        "/payroll/separation-checklist/",
        "/payroll/salary-revision/",
        "/payroll/allowance-maintenance/",
    ],
    "Leave": [
        "/leave/leave-request/",
        "/leave/leave-list/",
        "/leave/leave-approval/",
        "/leave/leave-type/",
        "/leave/leave-allocation/",
        "/leave/leave-balance/",
        "/leave/leave-holiday/",
        "/leave/leave-calendar/",
        "/leave/bulk-leave-request/",
        "/leave/leave-attachment/",
        "/leave/leave-encashment/",
        "/leave/leave-recall/",
    ],
    "Attendance": [
        "/attendance/attendance-request/",
        "/attendance/attendance-list/",
        "/attendance/shift-request/",
        "/attendance/shift-approve/",
        "/attendance/shift-assignment/",
        "/attendance/biometric-integration/",
        "/attendance/bulk-attendance/",
        "/attendance/attendance-calendar/",
    ],
}


def test_urls():
    """Test all URLs and report status"""
    client = Client()
    results = defaultdict(lambda: {"working": [], "missing": [], "error": []})

    print("\n" + "=" * 70)
    print("🧪 COMPREHENSIVE URL TESTING - All 106 URLs")
    print("=" * 70 + "\n")

    total_tested = 0
    total_working = 0

    for module, urls in URLS_TO_TEST.items():
        print(f"\n📋 Testing {module}...")
        print("-" * 50)

        for url in urls:
            total_tested += 1
            try:
                response = client.get(url)
                status_code = response.status_code

                if status_code == 404:
                    results[module]["missing"].append((url, status_code))
                    print(f"  ❌ {url:40} → 404 NOT FOUND")
                elif status_code == 500:
                    results[module]["error"].append((url, status_code))
                    print(f"  ⚠️  {url:40} → 500 SERVER ERROR")
                elif status_code in [200, 201, 301, 302, 303, 403]:
                    results[module]["working"].append((url, status_code))
                    print(f"  ✅ {url:40} → {status_code} OK")
                    total_working += 1
                else:
                    results[module]["error"].append((url, status_code))
                    print(f"  ⚠️  {url:40} → {status_code}")
            except Exception as e:
                results[module]["error"].append((url, str(e)))
                print(f"  ❌ {url:40} → ERROR: {str(e)[:30]}")

    # Print Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    total_missing = sum(len(v["missing"]) for v in results.values())
    total_errors = sum(len(v["error"]) for v in results.values())

    print(
        f"\n✅ Working URLs: {total_working}/{total_tested} ({100 * total_working // total_tested}%)"
    )
    print(f"❌ Missing URLs: {total_missing}/{total_tested}")
    print(f"⚠️  Error URLs: {total_errors}/{total_tested}")

    print("\n" + "=" * 70)
    print("DETAILED RESULTS BY MODULE")
    print("=" * 70)

    for module in sorted(results.keys()):
        data = results[module]
        total = len(data["working"]) + len(data["missing"]) + len(data["error"])
        working = len(data["working"])
        print(f"\n{module:20} : {working}/{total} ✅")
        
        if data['missing']:
            print("  Missing URLs:")
            for url, code in data['missing']:
                print(f"    • {url}")
        
        if data['error']:
            print("  Error URLs:")
            for url, code in data['error']:
                print(f"    • {url}")

    # Save detailed report
    with open("test_results_detailed.txt", "w") as f:
        f.write("URL TEST RESULTS\n")
        f.write("=" * 70 + "\n\n")
        for module in sorted(results.keys()):
            f.write(f"\n{module}\n")
            f.write("-" * 50 + "\n")
            data = results[module]
            for url, code in data["working"]:
                f.write(f"✅ {url} → {code}\n")
            for url, code in data["missing"]:
                f.write(f"❌ {url} → {code}\n")
            for url, code in data["error"]:
                f.write(f"⚠️  {url} → {code}\n")

    print("\n✅ Detailed results saved to 'test_results_detailed.txt'\n")


if __name__ == "__main__":
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    test_urls()
