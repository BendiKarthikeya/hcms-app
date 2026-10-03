"""
Test cases for Recruitment module
"""

from django.test import TestCase
from django.contrib.auth.models import User
from base.models import Company, Department, JobPosition, JobRole
from employee.models import Employee
from .models import Candidate, Recruitment, Stage, RecruitmentSurvey


class RecruitmentModelTest(TestCase):
    """Test cases for Recruitment model"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
        self.department = Department.objects.create(department="Test Department")
        self.job_position = JobPosition.objects.create(job_position="Test Position")
        self.job_role = JobRole.objects.create(job_role="Test Role")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.recruiter = Employee.objects.create(
            employee_first_name="Recruiter",
            employee_last_name="Test",
            email="recruiter@example.com",
            phone="+1234567890",
        )

    def test_recruitment_creation(self):
        """Test creating a recruitment process"""
        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            open_positions=5,
            recruiter=self.recruiter,
        )

        self.assertEqual(recruitment.title, "Software Engineer")
        self.assertEqual(recruitment.open_positions, 5)
        self.assertTrue(recruitment.is_active)

    def test_candidate_creation(self):
        """Test creating a candidate"""
        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=self.recruiter,
        )

        candidate = Candidate.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            mobile="+1234567890",
            recruitment_id=recruitment,
        )

        self.assertEqual(candidate.name, "John Doe")
        self.assertEqual(candidate.email, "john.doe@example.com")
        self.assertEqual(candidate.recruitment_id, recruitment)

    def test_stage_creation(self):
        """Test creating recruitment stages"""
        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=self.recruiter,
        )

        stage = Stage.objects.create(
            stage="Phone Screening",
            stage_type="initial",
            recruitment_id=recruitment,
            sequence=1,
        )

        self.assertEqual(stage.stage, "Phone Screening")
        self.assertEqual(stage.sequence, 1)
        self.assertEqual(stage.recruitment_id, recruitment)

    def test_recruitment_workflow(self):
        """Test complete recruitment workflow"""
        # Create recruitment
        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=self.recruiter,
        )

        # Create stages
        stage1 = Stage.objects.create(
            stage="Application Review",
            stage_type="initial",
            recruitment_id=recruitment,
            sequence=1,
        )

        stage2 = Stage.objects.create(
            stage="Technical Interview",
            stage_type="interview",
            recruitment_id=recruitment,
            sequence=2,
        )

        # Create candidate
        candidate = Candidate.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            mobile="+1234567890",
            recruitment_id=recruitment,
            stage_id=stage1,
        )

        # Move candidate to next stage
        candidate.stage_id = stage2
        candidate.save()

        self.assertEqual(candidate.stage_id, stage2)


class RecruitmentViewsTest(TestCase):
    """Test cases for Recruitment views"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.recruiter = Employee.objects.create(
            employee_first_name="Recruiter",
            employee_last_name="Test",
            email="recruiter@example.com",
            phone="+1234567890",
        )
        self.recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=self.recruiter,
        )

    def test_recruitment_list_view(self):
        """Test recruitment list view"""
        response = self.client.get("/recruitment/")
        self.assertEqual(response.status_code, 200)

    def test_recruitment_detail_view(self):
        """Test recruitment detail view"""
        response = self.client.get(f"/recruitment/{self.recruitment.id}/")
        self.assertEqual(response.status_code, 200)

    def test_candidate_create_view(self):
        """Test candidate creation view"""
        response = self.client.get("/recruitment/candidate/create/")
        self.assertEqual(response.status_code, 200)


class RecruitmentURLsTest(TestCase):
    """Test cases for Recruitment URLs"""

    def test_recruitment_urls(self):
        """Test recruitment URL patterns"""
        # Test main recruitment URL
        response = self.client.get("/recruitment/")
        self.assertEqual(response.status_code, 200)

        # Test candidate creation URL
        response = self.client.get("/recruitment/candidate/create/")
        self.assertEqual(response.status_code, 200)


class RecruitmentFormsTest(TestCase):
    """Test cases for Recruitment forms"""

    def test_candidate_form_validation(self):
        """Test candidate form validation"""
        from .forms import CandidateForm

        # Test valid form data
        form_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "mobile": "+1234567890",
        }

        form = CandidateForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid form data (invalid email)
        invalid_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "mobile": "+1234567890",
        }

        form = CandidateForm(data=invalid_data)
        self.assertFalse(form.is_valid())


class RecruitmentIntegrationTest(TestCase):
    """Integration tests for Recruitment module"""

    def setUp(self):
        """Set up test data"""
        self.recruiter = Employee.objects.create(
            employee_first_name="Recruiter",
            employee_last_name="Test",
            email="recruiter@example.com",
            phone="+1234567890",
        )

    def test_recruitment_pipeline(self):
        """Test complete recruitment pipeline"""
        # Create recruitment
        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=self.recruiter,
        )

        # Create stages
        stages = [
            Stage.objects.create(
                stage=f"Stage {i}",
                stage_type="interview",
                recruitment_id=recruitment,
                sequence=i,
            )
            for i in range(1, 4)
        ]

        # Create candidates
        candidates = []
        for i in range(10):
            candidate = Candidate.objects.create(
                name=f"Candidate {i}",
                email=f"candidate{i}@example.com",
                mobile=f"+123456789{i:02d}",
                recruitment_id=recruitment,
                stage_id=stages[i % 3],  # Distribute across stages
            )
            candidates.append(candidate)

        # Verify pipeline statistics
        self.assertEqual(Candidate.objects.count(), 10)
        self.assertEqual(recruitment.candidate_set.count(), 10)

        # Test stage distribution
        for stage in stages:
            stage_candidates = Candidate.objects.filter(stage_id=stage)
            self.assertGreater(len(stage_candidates), 0)


class RecruitmentPerformanceTest(TestCase):
    """Performance tests for Recruitment module"""

    def test_bulk_candidate_creation(self):
        """Test bulk candidate creation performance"""
        recruiter = Employee.objects.create(
            employee_first_name="Recruiter",
            employee_last_name="Test",
            email="recruiter@example.com",
            phone="+1234567890",
        )

        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=recruiter,
        )

        stage = Stage.objects.create(
            stage="Application Review",
            stage_type="initial",
            recruitment_id=recruitment,
            sequence=1,
        )

        # Create 100 candidates
        candidates = []
        for i in range(100):
            candidates.append(
                Candidate(
                    name=f"Candidate {i}",
                    email=f"candidate{i}@example.com",
                    mobile=f"+123456789{i:02d}",
                    recruitment_id=recruitment,
                    stage_id=stage,
                )
            )

        Candidate.objects.bulk_create(candidates)
        self.assertEqual(Candidate.objects.count(), 100)


class RecruitmentSurveyTest(TestCase):
    """Test cases for Recruitment Survey functionality"""

    def test_survey_creation(self):
        """Test creating recruitment surveys"""
        recruiter = Employee.objects.create(
            employee_first_name="Recruiter",
            employee_last_name="Test",
            email="recruiter@example.com",
            phone="+1234567890",
        )

        recruitment = Recruitment.objects.create(
            title="Software Engineer",
            description="Hiring software engineers",
            is_active=True,
            recruiter=recruiter,
        )

        survey = RecruitmentSurvey.objects.create(
            question="What is your experience with Django?",
            question_type="text",
            is_required=True,
            recruitment_id=recruitment,
        )

        self.assertEqual(survey.question, "What is your experience with Django?")
        self.assertEqual(survey.question_type, "text")
        self.assertTrue(survey.is_required)
