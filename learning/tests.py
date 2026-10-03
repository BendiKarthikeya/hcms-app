"""
Test cases for Learning & Development module
"""

from django.test import TestCase
from django.contrib.auth.models import User
from base.models import Company
from employee.models import Employee
from .models import (
    CourseCategory,
    TrainingCourse,
    CourseEnrollment,
    Skill,
    EmployeeSkill,
    Certification,
    EmployeeCertification,
    LearningPlan,
)


class LearningModelTest(TestCase):
    """Test cases for Learning & Development models"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
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

    def test_course_category_creation(self):
        """Test creating a course category"""
        category = CourseCategory.objects.create(
            name="Technical Training",
            description="Technical skills development",
            company=self.company,
        )

        self.assertEqual(category.name, "Technical Training")
        self.assertEqual(category.company, self.company)
        self.assertEqual(str(category), "Technical Training")

    def test_training_course_creation(self):
        """Test creating a training course"""
        category = CourseCategory.objects.create(
            name="Technical Training", company=self.company
        )

        course = TrainingCourse.objects.create(
            name="Python Programming",
            description="Learn Python programming",
            category=category,
            format="online",
            level="beginner",
            duration_hours=40,
            cost=500.00,
            instructor="Jane Smith",
            company=self.company,
        )

        self.assertEqual(course.name, "Python Programming")
        self.assertEqual(course.format, "online")
        self.assertEqual(course.level, "beginner")
        self.assertEqual(course.duration_hours, 40)

    def test_course_enrollment_creation(self):
        """Test creating a course enrollment"""
        category = CourseCategory.objects.create(
            name="Technical Training", company=self.company
        )

        course = TrainingCourse.objects.create(
            name="Python Programming",
            description="Learn Python programming",
            category=category,
            format="online",
            level="beginner",
            duration_hours=40,
            company=self.company,
        )

        enrollment = CourseEnrollment.objects.create(
            employee=self.employee, course=course, status="pending"
        )

        self.assertEqual(enrollment.employee, self.employee)
        self.assertEqual(enrollment.course, course)
        self.assertEqual(enrollment.status, "pending")

    def test_skill_creation(self):
        """Test creating a skill"""
        skill = Skill.objects.create(
            name="Python Programming",
            description="Python development skills",
            category="Technical",
        )

        self.assertEqual(skill.name, "Python Programming")
        self.assertEqual(skill.category, "Technical")

    def test_employee_skill_creation(self):
        """Test creating an employee skill"""
        skill = Skill.objects.create(name="Python Programming", category="Technical")

        employee_skill = EmployeeSkill.objects.create(
            employee=self.employee,
            skill=skill,
            proficiency_level="intermediate",
            years_experience=3,
        )

        self.assertEqual(employee_skill.employee, self.employee)
        self.assertEqual(employee_skill.skill, skill)
        self.assertEqual(employee_skill.proficiency_level, "intermediate")

    def test_certification_creation(self):
        """Test creating a certification"""
        certification = Certification.objects.create(
            name="Python Developer Certification",
            issuing_authority="Python Institute",
            validity_period_months=24,
        )

        self.assertEqual(certification.name, "Python Developer Certification")
        self.assertEqual(certification.issuing_authority, "Python Institute")

    def test_employee_certification_creation(self):
        """Test creating an employee certification"""
        certification = Certification.objects.create(
            name="Python Developer Certification", issuing_authority="Python Institute"
        )

        emp_cert = EmployeeCertification.objects.create(
            employee=self.employee,
            certification=certification,
            issue_date="2024-01-01",
            is_active=True,
        )

        self.assertEqual(emp_cert.employee, self.employee)
        self.assertEqual(emp_cert.certification, certification)
        self.assertTrue(emp_cert.is_active)

    def test_learning_plan_creation(self):
        """Test creating a learning plan"""
        learning_plan = LearningPlan.objects.create(
            employee=self.employee,
            title="2024 Development Plan",
            description="Professional development plan",
            start_date="2024-01-01",
            end_date="2024-12-31",
            status="planned",
            created_by=self.employee,
        )

        self.assertEqual(learning_plan.employee, self.employee)
        self.assertEqual(learning_plan.title, "2024 Development Plan")
        self.assertEqual(learning_plan.status, "planned")


class LearningViewTest(TestCase):
    """Test cases for Learning & Development views"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
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

    def test_course_list_view(self):
        """Test course list view"""
        response = self.client.get("/learning/courses/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Login and test again
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/learning/courses/")
        self.assertEqual(response.status_code, 200)

    def test_my_enrollments_view(self):
        """Test my enrollments view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/learning/my-enrollments/")
        self.assertEqual(response.status_code, 200)

    def test_my_skills_view(self):
        """Test my skills view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/learning/my-skills/")
        self.assertEqual(response.status_code, 200)


class LearningIntegrationTest(TestCase):
    """Integration tests for Learning & Development module"""

    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
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

    def test_complete_learning_workflow(self):
        """Test complete learning workflow"""
        # Create course category
        category = CourseCategory.objects.create(
            name="Technical Training", company=self.company
        )

        # Create training course
        course = TrainingCourse.objects.create(
            name="Python Programming",
            description="Learn Python programming",
            category=category,
            format="online",
            level="beginner",
            duration_hours=40,
            company=self.company,
        )

        # Enroll employee
        enrollment = CourseEnrollment.objects.create(
            employee=self.employee, course=course, status="approved"
        )

        # Update progress
        enrollment.progress_percentage = 50
        enrollment.save()

        # Complete course
        enrollment.status = "completed"
        enrollment.completion_date = "2024-06-30"
        enrollment.final_score = 85.5
        enrollment.certificate_issued = True
        enrollment.save()

        # Verify completion
        self.assertEqual(enrollment.status, "completed")
        self.assertEqual(enrollment.progress_percentage, 50)
        self.assertEqual(enrollment.final_score, 85.5)
        self.assertTrue(enrollment.certificate_issued)
