"""Curated product knowledge and page routing for the sitewide chatbot."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable


PRODUCT_OVERVIEW = (
    "FITS HCMS is a multi-module HR platform built on Django. It includes core "
    "HR, employee management, recruitment, onboarding, leave, attendance, "
    "biometric integrations, payroll, learning, talent and succession, "
    "offboarding, expenses, reporting, audit, and regional compliance modules."
)


@dataclass(frozen=True)
class FeatureEntry:
    title: str
    description: str
    keywords: tuple[str, ...]
    route_name: str | None = None
    fallback_path: str | None = None
    module: str = "general"
    phrases: tuple[str, ...] = field(default_factory=tuple)

    def path(self) -> str | None:
        return self.fallback_path

    def url(self, base_url: str) -> str | None:
        p = self.path()
        if not p:
            return None
        return f"{base_url.rstrip('/')}{p}"


FEATURES: tuple[FeatureEntry, ...] = (
    FeatureEntry(
        title="Organization Chart",
        description="View the company hierarchy, reporting structure, and org chart.",
        keywords=(
            "organization",
            "organisation",
            "hierarchy",
            "org",
            "chart",
            "reporting",
            "structure",
            "manager",
            "tree",
        ),
        phrases=(
            "organization chart",
            "organisation chart",
            "org chart",
            "reporting hierarchy",
            "company hierarchy",
        ),
        route_name="organisation-chart",
        fallback_path="/employee/organisation-chart/",
        module="employee",
    ),
    FeatureEntry(
        title="Employee Profile",
        description="Open your employee profile and personal HR information.",
        keywords=("profile", "employee", "my", "personal", "details"),
        phrases=("employee profile", "my profile"),
        route_name="employee-profile",
        fallback_path="/employee/employee-profile/",
        module="employee",
    ),
    FeatureEntry(
        title="Employees Directory",
        description="Browse and manage employee records.",
        keywords=("employees", "directory", "employee", "staff", "list"),
        phrases=("employee list", "employees page", "employee directory"),
        route_name="employee-view",
        fallback_path="/employee/employee-view/",
        module="employee",
    ),
    FeatureEntry(
        title="Manager Dashboard",
        description="Open the manager portal dashboard for team oversight.",
        keywords=("manager", "dashboard", "team", "portal"),
        phrases=("manager dashboard", "manager portal"),
        route_name="manager-dashboard",
        fallback_path="/employee/manager-dashboard/",
        module="employee",
    ),
    FeatureEntry(
        title="Document Requests",
        description="View and manage employee document requests.",
        keywords=("document", "documents", "request", "letter", "certificate"),
        phrases=("document requests", "employee documents"),
        route_name="document-request-view",
        fallback_path="/employee/document-request-view/",
        module="employee",
    ),
    FeatureEntry(
        title="Shift Requests",
        description="Review or raise shift change requests.",
        keywords=("shift", "request", "schedule", "roster"),
        phrases=("shift requests", "shift change"),
        route_name="shift-request-view",
        fallback_path="/employee/shift-request-view/",
        module="employee",
    ),
    FeatureEntry(
        title="Work Type Requests",
        description="Manage work type requests such as remote, office, or hybrid changes.",
        keywords=("work", "type", "request", "remote", "hybrid", "office"),
        phrases=("work type requests", "remote work request"),
        route_name="work-type-request-view",
        fallback_path="/employee/work-type-request-view/",
        module="employee",
    ),
    FeatureEntry(
        title="Policies",
        description="Read company policies and disciplinary documents.",
        keywords=("policy", "policies", "disciplinary", "rules", "handbook"),
        phrases=("company policies", "employee policies"),
        route_name="view-policies",
        fallback_path="/employee/view-policies/",
        module="employee",
    ),
    FeatureEntry(
        title="Recruitment Dashboard",
        description="Open the recruitment dashboard and hiring overview.",
        keywords=("recruitment", "hiring", "dashboard", "jobs"),
        phrases=("recruitment dashboard", "hiring dashboard"),
        route_name="recruitment-dashboard",
        fallback_path="/recruitment/dashboard",
        module="recruitment",
    ),
    FeatureEntry(
        title="Raise Recruitment Request",
        description="Create a new recruitment request or open a new job requisition.",
        keywords=("raise", "create", "new", "recruitment", "request", "requisition", "job", "open"),
        phrases=("raise recruitment", "new recruitment request", "create recruitment", "open recruitment"),
        route_name="raise-recruitment",
        fallback_path="/employee/raise-recruitment/",
        module="recruitment",
    ),
    FeatureEntry(
        title="View Recruitment Requests",
        description="View and manage all submitted recruitment requests.",
        keywords=("view", "recruitment", "requests", "request", "list", "manage"),
        phrases=("view recruitment requests", "recruitment requests", "recruitment request list"),
        route_name="recruitment-view",
        fallback_path="/recruitment/recruitment-view",
        module="recruitment",
    ),
    FeatureEntry(
        title="Recruitment Pipeline",
        description="Track candidates through the recruitment pipeline.",
        keywords=("recruitment", "pipeline", "candidate", "kanban", "stage"),
        phrases=("recruitment pipeline", "candidate pipeline"),
        route_name="pipeline",
        fallback_path="/recruitment/pipeline/",
        module="recruitment",
    ),
    FeatureEntry(
        title="Candidates",
        description="Browse candidate records and applications.",
        keywords=("candidate", "candidates", "application", "applicants"),
        phrases=("candidate list", "candidates page"),
        route_name="candidate-view",
        fallback_path="/recruitment/candidate-view/",
        module="recruitment",
    ),
    FeatureEntry(
        title="Interviews",
        description="Schedule and review interviews.",
        keywords=("interview", "interviews", "schedule", "panel"),
        phrases=("interview schedule", "interviews page"),
        route_name="interview-view",
        fallback_path="/recruitment/interview-view/",
        module="recruitment",
    ),
    FeatureEntry(
        title="Open Jobs",
        description="View published or open recruitment positions.",
        keywords=("open", "jobs", "positions", "vacancies"),
        phrases=("open jobs", "job openings"),
        route_name="open-recruitments",
        fallback_path="/recruitment/open-recruitments",
        module="recruitment",
    ),
    FeatureEntry(
        title="CV Screening",
        description="Use AI-assisted CV screening and candidate ranking.",
        keywords=("cv", "screening", "resume", "resumes", "ai", "ranking"),
        phrases=("cv screening", "candidate ranking", "resume screening"),
        route_name="cv-screening",
        fallback_path="/recruitment/cv-screening/",
        module="recruitment",
    ),
    FeatureEntry(
        title="Onboarding",
        description="Manage onboarding workflows, tasks, and new joiners.",
        keywords=("onboarding", "new", "joiner", "preboarding", "checklist"),
        phrases=("onboarding", "new joiner onboarding"),
        route_name="onboarding-view",
        fallback_path="/onboarding/onboarding-view/",
        module="onboarding",
    ),
    FeatureEntry(
        title="Leave Dashboard",
        description="Open the leave dashboard for balances, requests, and approvals.",
        keywords=("leave", "dashboard", "time", "off", "vacation"),
        phrases=("leave dashboard", "time off dashboard"),
        route_name="leave-dashboard",
        fallback_path="/leave/leave-dashboard",
        module="leave",
    ),
    FeatureEntry(
        title="My Leave Requests",
        description="View your own leave requests and leave history.",
        keywords=("my", "leave", "request", "requests", "vacation"),
        phrases=("my leave requests", "my leave history"),
        route_name="user-request-view",
        fallback_path="/leave/user-request-view/",
        module="leave",
    ),
    FeatureEntry(
        title="Leave Requests",
        description="Review and manage employee leave requests.",
        keywords=("leave", "requests", "approval", "approve", "vacation"),
        phrases=("leave requests", "leave approvals"),
        route_name="request-view",
        fallback_path="/leave/request-view/",
        module="leave",
    ),
    FeatureEntry(
        title="Leave Policy Engine",
        description="Configure leave policy rules and workflow behavior.",
        keywords=("leave", "policy", "engine", "rules", "workflow"),
        phrases=("leave policy engine", "leave rules"),
        route_name="leave-policy-engine",
        fallback_path="/leave/policy-engine/",
        module="leave",
    ),
    FeatureEntry(
        title="Leave Types",
        description="Manage leave types and leave configuration.",
        keywords=("leave", "types", "type", "configuration"),
        phrases=("leave types", "leave setup"),
        route_name="type-view",
        fallback_path="/leave/type-view/",
        module="leave",
    ),
    FeatureEntry(
        title="Holidays",
        description="View and manage holiday calendars.",
        keywords=("holiday", "holidays", "calendar"),
        phrases=("holiday calendar", "company holidays"),
        route_name="holiday-view",
        fallback_path="/configuration/holiday-view",
        module="leave",
    ),
    FeatureEntry(
        title="Attendance",
        description="Open the attendance module for check-ins, logs, and tracking.",
        keywords=("attendance", "check", "in", "out", "time", "tracking"),
        phrases=("attendance page", "check in", "attendance logs"),
        fallback_path="/attendance/",
        module="attendance",
    ),
    FeatureEntry(
        title="Biometric Devices",
        description="Manage biometric devices and employee-device mappings.",
        keywords=(
            "biometric",
            "devices",
            "device",
            "fingerprint",
            "face",
            "zk",
            "cosec",
            "dahua",
        ),
        phrases=("biometric settings", "biometric devices"),
        fallback_path="/biometric/",
        module="biometric",
    ),
    FeatureEntry(
        title="Payroll Dashboard",
        description="Open the payroll dashboard for payroll operations and summaries.",
        keywords=("payroll", "salary", "dashboard", "compensation"),
        phrases=("payroll dashboard", "salary dashboard"),
        route_name="view-payroll-dashboard",
        fallback_path="/payroll/view-payroll-dashboard/",
        module="payroll",
    ),
    FeatureEntry(
        title="Contracts",
        description="Manage employee payroll contracts.",
        keywords=("contract", "contracts", "salary", "employment"),
        phrases=("payroll contract", "employee contract"),
        route_name="view-contract",
        fallback_path="/payroll/view-contract/",
        module="payroll",
    ),
    FeatureEntry(
        title="Allowances",
        description="Manage payroll allowance components.",
        keywords=("allowance", "allowances", "pay", "component"),
        phrases=("payroll allowances", "allowance setup"),
        route_name="view-allowance",
        fallback_path="/payroll/view-allowance/",
        module="payroll",
    ),
    FeatureEntry(
        title="Deductions",
        description="Manage payroll deduction components.",
        keywords=("deduction", "deductions", "payroll", "component"),
        phrases=("payroll deductions", "deduction setup"),
        route_name="view-deduction",
        fallback_path="/payroll/view-deduction/",
        module="payroll",
    ),
    FeatureEntry(
        title="Payslips",
        description="View and process employee payslips.",
        keywords=("payslip", "payslips", "salary slip", "salary"),
        phrases=("payslips", "salary slips"),
        route_name="view-payslip",
        fallback_path="/payroll/view-payslip/",
        module="payroll",
    ),
    FeatureEntry(
        title="Loans and Advances",
        description="Manage payroll loans and advanced salary requests.",
        keywords=("loan", "loans", "advance", "advanced", "salary"),
        phrases=("loan management", "advanced salary"),
        route_name="view-loan",
        fallback_path="/payroll/view-loan/",
        module="payroll",
    ),
    FeatureEntry(
        title="Reimbursements",
        description="Manage reimbursement and encashment workflows.",
        keywords=("reimbursement", "reimbursements", "encashment", "expense", "claim"),
        phrases=("reimbursements", "encashments"),
        route_name="view-reimbursement",
        fallback_path="/payroll/view-reimbursement/",
        module="payroll",
    ),
    FeatureEntry(
        title="Federal Tax",
        description="Open payroll federal tax and filing status settings.",
        keywords=("tax", "federal", "filing", "status"),
        phrases=("federal tax", "filing status"),
        route_name="filing-status-view",
        fallback_path="/payroll/filing-status-view/",
        module="payroll",
    ),
    FeatureEntry(
        title="End-of-Service Benefits",
        description="Calculate and manage EOSB or gratuity records.",
        keywords=("eosb", "gratuity", "end", "service", "benefit", "benefits"),
        phrases=("end of service benefits", "gratuity calculation", "eosb"),
        route_name="eosb-list",
        fallback_path="/payroll/eosb-list/",
        module="payroll",
    ),
    FeatureEntry(
        title="Wage Protection System",
        description="Generate and manage WPS files and exceptions.",
        keywords=("wps", "wage", "protection", "salary", "bank", "file"),
        phrases=("wage protection system", "wps files"),
        route_name="wps-file-list",
        fallback_path="/payroll/wps-file-list/",
        module="payroll",
    ),
    FeatureEntry(
        title="GL Integration",
        description="Manage payroll general ledger integrations.",
        keywords=("gl", "ledger", "integration", "finance", "accounting"),
        phrases=("gl integration", "general ledger"),
        route_name="gl-integration",
        fallback_path="/payroll/gl-integration/",
        module="payroll",
    ),
    FeatureEntry(
        title="ICBS Disbursement",
        description="Process payroll disbursement integrations through ICBS.",
        keywords=("icbs", "disbursement", "bank", "payment", "integration"),
        phrases=("icbs integration", "payroll disbursement"),
        route_name="icbs-integration",
        fallback_path="/payroll/icbs-integration/",
        module="payroll",
    ),
    FeatureEntry(
        title="Performance Dashboard",
        description="Open the PMS dashboard for goals, reviews, and feedback.",
        keywords=("performance", "pms", "dashboard", "review"),
        phrases=("performance dashboard", "pms dashboard"),
        route_name="dashboard-view",
        fallback_path="/pms/dashboard-view",
        module="pms",
    ),
    FeatureEntry(
        title="Objectives and KPIs",
        description="Manage performance objectives, KPIs, and goals.",
        keywords=("objective", "objectives", "kpi", "kpis", "goal", "goals"),
        phrases=("objectives", "kpis", "goal tracking"),
        route_name="objective-list-view",
        fallback_path="/pms/objective-list-view/",
        module="pms",
    ),
    FeatureEntry(
        title="Key Results",
        description="Track key results and progress toward goals.",
        keywords=("key", "result", "results", "okr", "progress"),
        phrases=("key results", "okr tracking"),
        route_name="view-key-result",
        fallback_path="/pms/view-key-result/",
        module="pms",
    ),
    FeatureEntry(
        title="360 Feedback",
        description="Review feedback cycles and performance feedback records.",
        keywords=("feedback", "360", "review", "peer", "manager"),
        phrases=("360 feedback", "performance feedback"),
        route_name="feedback-view",
        fallback_path="/pms/feedback-view/",
        module="pms",
    ),
    FeatureEntry(
        title="Review Cycles",
        description="Manage performance review periods and cycles.",
        keywords=("review", "cycle", "period", "appraisal"),
        phrases=("review cycles", "appraisal periods"),
        route_name="period-view",
        fallback_path="/pms/period-view",
        module="pms",
    ),
    FeatureEntry(
        title="Performance Improvement Plans",
        description="Create and manage PIP workflows.",
        keywords=("pip", "improvement", "performance", "plan"),
        phrases=("pip management", "performance improvement plan"),
        route_name="pip-list",
        fallback_path="/pms/pip-list/",
        module="pms",
    ),
    FeatureEntry(
        title="Learning Dashboard",
        description="Open the learning and development dashboard.",
        keywords=("learning", "training", "dashboard", "development"),
        phrases=("learning dashboard", "l&d dashboard"),
        route_name="learning:dashboard",
        fallback_path="/learning/dashboard/",
        module="learning",
    ),
    FeatureEntry(
        title="Training Courses",
        description="Browse and enroll in training courses.",
        keywords=("training", "course", "courses", "learning", "enroll"),
        phrases=("training courses", "course list"),
        route_name="learning:course_list",
        fallback_path="/learning/courses/",
        module="learning",
    ),
    FeatureEntry(
        title="My Enrollments",
        description="View the courses you are enrolled in.",
        keywords=("enrollment", "enrollments", "my", "courses"),
        phrases=("my enrollments", "course enrollments"),
        route_name="learning:my_enrollments",
        fallback_path="/learning/my-enrollments/",
        module="learning",
    ),
    FeatureEntry(
        title="Assessments",
        description="Open learning assessments and evaluations.",
        keywords=("assessment", "assessments", "quiz", "evaluation"),
        phrases=("learning assessments", "course assessments"),
        route_name="learning:assessments",
        fallback_path="/learning/assessments/",
        module="learning",
    ),
    FeatureEntry(
        title="Expenses Dashboard",
        description="Open the expenses and travel dashboard.",
        keywords=("expense", "expenses", "travel", "dashboard", "claim"),
        phrases=("expenses dashboard", "travel dashboard"),
        route_name="expenses:dashboard",
        fallback_path="/expenses/",
        module="expenses",
    ),
    FeatureEntry(
        title="Travel Requests",
        description="Manage travel requests and travel approvals.",
        keywords=("travel", "request", "requests", "trip"),
        phrases=("travel requests", "trip requests"),
        route_name="expenses:travel_request_list",
        fallback_path="/expenses/travel-requests/",
        module="expenses",
    ),
    FeatureEntry(
        title="Expense Claims",
        description="Manage employee expense claims and reimbursements.",
        keywords=("expense", "claims", "claim", "reimbursement"),
        phrases=("expense claims", "expense reimbursement"),
        route_name="expenses:expense_claim_list",
        fallback_path="/expenses/expense-claims/",
        module="expenses",
    ),
    FeatureEntry(
        title="My Expense Claims",
        description="View your own submitted expense claims.",
        keywords=("my", "expense", "claims", "claim"),
        phrases=("my expense claims", "my claims"),
        route_name="expenses:my_expense_claims",
        fallback_path="/expenses/my-expense-claims/",
        module="expenses",
    ),
    FeatureEntry(
        title="Talent Dashboard",
        description="Open the talent and succession dashboard.",
        keywords=("talent", "succession", "dashboard", "hipo"),
        phrases=("talent dashboard", "succession dashboard"),
        route_name="talent:dashboard",
        fallback_path="/talent/dashboard/",
        module="talent",
    ),
    FeatureEntry(
        title="Talent Profiles",
        description="Browse talent profiles and readiness details.",
        keywords=("talent", "profiles", "profile", "readiness"),
        phrases=("talent profiles", "succession profiles"),
        route_name="talent:profile_list",
        fallback_path="/talent/profiles/",
        module="talent",
    ),
    FeatureEntry(
        title="Critical Roles",
        description="View critical roles for succession planning.",
        keywords=("critical", "roles", "succession", "role"),
        phrases=("critical roles", "succession roles"),
        route_name="talent:critical_role_list",
        fallback_path="/talent/critical-roles/",
        module="talent",
    ),
    FeatureEntry(
        title="Succession Plans",
        description="Open succession planning records and plan details.",
        keywords=("succession", "plan", "plans", "replacement"),
        phrases=("succession plans", "succession planning"),
        route_name="talent:succession_plan_list",
        fallback_path="/talent/succession-plans/",
        module="talent",
    ),
    FeatureEntry(
        title="Career Paths",
        description="Explore talent career paths and progression mapping.",
        keywords=("career", "path", "paths", "growth"),
        phrases=("career paths", "career progression"),
        fallback_path="/talent/career-paths/",
        module="talent",
    ),
    FeatureEntry(
        title="9-Box Matrix",
        description="Open the 9-box talent matrix view.",
        keywords=("9-box", "nine-box", "matrix", "talent"),
        phrases=("9-box matrix", "nine box"),
        fallback_path="/talent/9-box-matrix/",
        module="talent",
    ),
    FeatureEntry(
        title="IDP Generation",
        description="Manage individual development plans.",
        keywords=("idp", "development", "plan", "individual"),
        phrases=("idp", "individual development plan"),
        fallback_path="/talent/idp/",
        module="talent",
    ),
    FeatureEntry(
        title="High-Potential Tracking",
        description="Track high-potential employees and succession readiness.",
        keywords=("high", "potential", "hipo", "hi-po", "tracking"),
        phrases=("high-potential tracking", "hipo"),
        fallback_path="/talent/high-potential/",
        module="talent",
    ),
    FeatureEntry(
        title="Offboarding Dashboard",
        description="Open the offboarding dashboard and exit workflow.",
        keywords=("offboarding", "exit", "dashboard", "separation"),
        phrases=("offboarding dashboard", "exit process"),
        route_name="offboarding-dashboard",
        fallback_path="/offboarding/dashboard",
        module="offboarding",
    ),
    FeatureEntry(
        title="Resignation Letters",
        description="Review employee resignation letters and resignation requests.",
        keywords=("resignation", "letter", "letters", "resign"),
        phrases=("resignation letters", "resignation requests"),
        route_name="resignation-request-view",
        fallback_path="/offboarding/resignation-requests-view/",
        module="offboarding",
    ),
    FeatureEntry(
        title="Omani Compliance",
        description="Manage Oman-specific compliance configuration, audit, and reports.",
        keywords=("oman", "omani", "compliance", "audit", "tax"),
        phrases=("omani compliance", "oman labour compliance"),
        fallback_path="/omani-compliance/",
        module="compliance",
    ),
)


def _normalize(text: str) -> str:
    cleaned = []
    for char in text.lower():
        cleaned.append(char if char.isalnum() else " ")
    return " ".join("".join(cleaned).split())


def _tokenize(text: str) -> set[str]:
    return set(_normalize(text).split())


def _score_feature(query: str, feature: FeatureEntry) -> float:
    query_normalized = _normalize(query)
    query_tokens = _tokenize(query)
    feature_tokens = (
        set(feature.keywords)
        | _tokenize(feature.title)
        | _tokenize(feature.description)
    )

    overlap = len(query_tokens & feature_tokens)
    score = overlap * 3.0

    for phrase in feature.phrases:
        if _normalize(phrase) in query_normalized:
            score += 8.0

    title_ratio = SequenceMatcher(
        None, query_normalized, _normalize(feature.title)
    ).ratio()
    score += title_ratio * 2.0

    return score


def rank_features(query: str, limit: int = 6) -> list[FeatureEntry]:
    scored = []
    for feature in FEATURES:
        score = _score_feature(query, feature)
        if score > 0:
            scored.append((score, feature))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [feature for _, feature in scored[:limit]]


def build_links(
    base_url: str, features: Iterable[FeatureEntry]
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for feature in features:
        path = feature.path()
        if not path or path in seen:
            continue
        seen.add(path)
        links.append(
            {
                "title": feature.title,
                "path": path,
                "description": feature.description,
                "module": feature.module,
            }
        )
    return links


def build_fallback_answer(question: str, base_url: str) -> dict[str, object]:
    matches = rank_features(question)
    links = build_links(base_url, matches)

    if links:
        first = links[0]
        lines = [
            f"The best match for that is {first['title']}.",
            first["description"],
        ]
        if len(links) > 1:
            lines.append("")
            lines.append("You may also want:")
            for link in links[1:4]:
                lines.append(f"- {link['title']}.")
    else:
        lines = [
            "I can help with FITS HCMS product navigation and feature questions.",
            "Try asking about modules like employee profile, org chart, recruitment pipeline, attendance, payroll, EOSB, WPS, learning, or succession planning.",
        ]

    return {
        "answer": "\n".join(lines),
        "links": links,
        "matches": [feature.title for feature in matches],
    }
