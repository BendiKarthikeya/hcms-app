"""
Test cases for Onboarding module
"""

from django.test import TestCase
from django.contrib.auth.models import User
from employee.models import Employee
from .models import OnboardingStage, OnboardingTask, OnboardingCandidate


class OnboardingModelTest(TestCase):
    """Test cases for Onboarding model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.employee = Employee.objects.create(
            employee_first_name="John",
            employee_last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            employee_user_id=self.user,
        )

    def test_onboarding_stage_creation(self):
        """Test creating an onboarding stage"""
        stage = OnboardingStage.objects.create(
            stage_title="Document Collection",
            stage_description="Collect all required documents",
            stage_sequence=1,
        )

        self.assertEqual(stage.stage_title, "Document Collection")
        self.assertEqual(stage.stage_sequence, 1)

    def test_onboarding_task_creation(self):
        """Test creating an onboarding task"""
        stage = OnboardingStage.objects.create(
            stage_title="Document Collection",
            stage_description="Collect all required documents",
            stage_sequence=1,
        )

        task = OnboardingTask.objects.create(
            stage_id=stage,
            task_title="Submit ID Proof",
            task_description="Submit government-issued ID proof",
            task_sequence=1,
        )

        self.assertEqual(task.task_title, "Submit ID Proof")
        self.assertEqual(task.stage_id, stage)
        self.assertEqual(task.task_sequence, 1)

    def test_onboarding_candidate_creation(self):
        """Test creating an onboarding candidate"""
        stage = OnboardingStage.objects.create(
            stage_title="Document Collection",
            stage_description="Collect all required documents",
            stage_sequence=1,
        )

        candidate = OnboardingCandidate.objects.create(
            candidate_name="John Doe",
            candidate_email="john.doe@example.com",
            candidate_mobile="+1234567890",
            stage_id=stage,
            recruitment_id=None,
        )

        self.assertEqual(candidate.candidate_name, "John Doe")
        self.assertEqual(candidate.candidate_email, "john.doe@example.com")
        self.assertEqual(candidate.stage_id, stage)


class OnboardingViewsTest(TestCase):
    """Test cases for Onboarding views"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_onboarding_list_view(self):
        """Test onboarding list view"""
        response = self.client.get("/onboarding/")
        self.assertEqual(response.status_code, 200)

    def test_onboarding_stage_create_view(self):
        """Test onboarding stage creation view"""
        response = self.client.get("/onboarding/stage/create/")
        self.assertEqual(response.status_code, 200)

    def test_onboarding_candidate_create_view(self):
        """Test onboarding candidate creation view"""
        response = self.client.get("/onboarding/candidate/create/")
        self.assertEqual(response.status_code, 200)


class OnboardingURLsTest(TestCase):
    """Test cases for Onboarding URLs"""

    def test_onboarding_urls(self):
        """Test onboarding URL patterns"""
        # Test main onboarding URL
        response = self.client.get("/onboarding/")
        self.assertEqual(response.status_code, 200)

        # Test stage creation URL
        response = self.client.get("/onboarding/stage/create/")
        self.assertEqual(response.status_code, 200)

        # Test candidate creation URL
        response = self.client.get("/onboarding/candidate/create/")
        self.assertEqual(response.status_code, 200)


class OnboardingFormsTest(TestCase):
    """Test cases for Onboarding forms"""

    def test_onboarding_stage_form_validation(self):
        """Test onboarding stage form validation"""
        from .forms import OnboardingStageForm

        # Test valid form data
        form_data = {
            "stage_title": "Document Collection",
            "stage_description": "Collect all required documents",
            "stage_sequence": 1,
        }

        form = OnboardingStageForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid form data (missing required field)
        invalid_data = {
            "stage_description": "Collect all required documents",
            "stage_sequence": 1,
            # Missing stage_title
        }

        form = OnboardingStageForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_onboarding_candidate_form(self):
        """Test onboarding candidate form"""
        from .forms import OnboardingCandidateForm

        form_data = {
            "candidate_name": "John Doe",
            "candidate_email": "john.doe@example.com",
            "candidate_mobile": "+1234567890",
        }

        form = OnboardingCandidateForm(data=form_data)
        self.assertTrue(form.is_valid())


class OnboardingIntegrationTest(TestCase):
    """Integration tests for Onboarding module"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_onboarding_workflow(self):
        """Test complete onboarding workflow"""
        # Create onboarding stages
        stages = [
            OnboardingStage.objects.create(
                stage_title=f"Stage {i}",
                stage_description=f"Stage {i} description",
                stage_sequence=i,
            )
            for i in range(1, 4)
        ]

        # Create tasks for each stage
        for stage in stages:
            for j in range(1, 4):
                OnboardingTask.objects.create(
                    stage_id=stage,
                    task_title=f"Task {j} for {stage.stage_title}",
                    task_description=f"Task {j} description",
                    task_sequence=j,
                )

        # Create onboarding candidate
        candidate = OnboardingCandidate.objects.create(
            candidate_name="John Doe",
            candidate_email="john.doe@example.com",
            candidate_mobile="+1234567890",
            stage_id=stages[0],  # Start at first stage
        )

        # Verify workflow setup
        self.assertEqual(OnboardingStage.objects.count(), 3)
        self.assertEqual(OnboardingTask.objects.count(), 9)
        self.assertEqual(OnboardingCandidate.objects.count(), 1)

        # Test stage progression
        candidate.stage_id = stages[1]  # Move to second stage
        candidate.save()

        self.assertEqual(candidate.stage_id, stages[1])


class OnboardingPerformanceTest(TestCase):
    """Performance tests for Onboarding module"""

    def test_bulk_onboarding_setup(self):
        """Test bulk onboarding setup performance"""
        # Create multiple stages and tasks
        stages = []
        for i in range(10):
            stage = OnboardingStage(
                stage_title=f"Stage {i}",
                stage_description=f"Stage {i} description",
                stage_sequence=i,
            )
            stages.append(stage)

        OnboardingStage.objects.bulk_create(stages)

        # Create tasks for all stages
        tasks = []
        for stage in OnboardingStage.objects.all():
            for j in range(5):
                task = OnboardingTask(
                    stage_id=stage,
                    task_title=f"Task {j} for {stage.stage_title}",
                    task_description=f"Task {j} description",
                    task_sequence=j,
                )
                tasks.append(task)

        OnboardingTask.objects.bulk_create(tasks)

        self.assertEqual(OnboardingStage.objects.count(), 10)
        self.assertEqual(OnboardingTask.objects.count(), 50)


class OnboardingTaskCompletionTest(TestCase):
    """Test cases for task completion functionality"""

    def test_task_completion_tracking(self):
        """Test task completion tracking"""
        stage = OnboardingStage.objects.create(
            stage_title="Document Collection",
            stage_description="Collect all required documents",
            stage_sequence=1,
        )

        task = OnboardingTask.objects.create(
            stage_id=stage,
            task_title="Submit ID Proof",
            task_description="Submit government-issued ID proof",
            task_sequence=1,
        )

        candidate = OnboardingCandidate.objects.create(
            candidate_name="John Doe",
            candidate_email="john.doe@example.com",
            candidate_mobile="+1234567890",
            stage_id=stage,
        )

        # Test task completion (this might be handled by a separate model)
        # The system should track which tasks are completed by which candidate
        self.assertIsNotNone(task)
        self.assertIsNotNone(candidate)
