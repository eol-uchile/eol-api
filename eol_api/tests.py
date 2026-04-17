#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Libraries
import datetime
import json

# Installed packages (via pip)
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import now, timedelta
from mock import patch
from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application
from rest_framework.test import APIClient

# Edx dependencies
from common.djangoapps.student.tests.factories import UserFactory
from edxucursos.models import EdxUCursosMapping
from lms.djangoapps.grades.models import PersistentCourseGrade
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

# Internal project dependencies
from .models import ClientCourseAccess
from .serializers import StudentGradesSerializer

@override_settings(EOL_API_RATE='10/minute')
class TestStudentGradesSerializer(ModuleStoreTestCase):
    def setUp(self):
        super(TestStudentGradesSerializer, self).setUp()
        self.course = CourseFactory.create(
            org='mss',
            course='999',
            display_name='2022',
            emit_signals=True)
        aux = CourseOverview.get_from_id(self.course.id)
        self.course_2 = CourseFactory.create(
            org='mss',
            course='101',
            display_name='2025',
            emit_signals=True)
        aux_2 = CourseOverview.get_from_id(self.course_2.id)
        self.course_3 = CourseFactory.create(
            org='mss',
            course='131',
            display_name='2025',
            emit_signals=True)
        aux_3 = CourseOverview.get_from_id(self.course_3.id)
        with patch('common.djangoapps.student.models.cc.User.save'):
            # staff user
            self.user_staff = UserFactory(
                username='testuser3',
                password='12345',
                email='student2@edx.org',
                is_staff=True)
        self.application = Application.objects.create(
            client_id="aaaaaaaaaaaaa",
            user = self.user_staff,
            client_type = Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
            client_secret="bbbbbbbbb",
            name="test_eol_api"
        )
        self.client_token = APIClient()
        self.token = AccessToken.objects.create(
            user=self.user_staff,
            application=self.application,
            token="test-token",
            expires=now() + timedelta(hours=1),
            scope="read write"
        )
        ClientCourseAccess.objects.create(
            client = self.application,
            course_id = str(self.course.id),
            created = datetime.datetime.now(),
            created_by = self.user_staff
        )
        ClientCourseAccess.objects.create(
            client = self.application,
            course_id = str(self.course_3.id),
            created = datetime.datetime.now(),
            created_by = self.user_staff
        )

    def test_eol_api_student_grades_serializers(self):
        """
        test course serializers normal process with only required attribute
        """
        body = {
            "course_id":str(self.course.id)
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertTrue(serializer.is_valid())

    def test_eol_api_course_serializers_no_params(self):
        """
        test course serializers when there is not data in body post
        """
        body = {}
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["course_id"][0]), "This field is required.")

    def test_eol_api_course_serializers_wrong_course_id(self):
        """
        test course serializers when there is a not valid course_id
        """
        wrong_id = "test/111"
        body = {
            "course_id": wrong_id
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        expected = f"Course key not valid or dont exists: {wrong_id}"
        self.assertEqual(str(serializer.errors["course_id"][0]), expected)

    def test_eol_api_course_serializers_from_date(self):
        """
        test course serializers using different from_date values
        1. Not null attribute
        2. Wrong format
        3. Future date
        4. Normal process
        """
        # 1 Not null attribute
        body = {
            "course_id":str(self.course.id),
            "from_date":None
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["from_date"][0]), "This field may not be null.")

        # 2 Wrong format
        body = {
            "course_id":str(self.course.id),
            "from_date":"2020/07/07"
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["from_date"][0]), "Date has wrong format. Use one of these formats instead: YYYY-MM-DD, YYYY-MM-DD hh:mm, YYYY-MM-DD hh:mm:ss.")
        # 3 Future date
        body = {
            "course_id":str(self.course.id),
            "from_date":"2027-07-20"
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["from_date"][0]), "from_date can´t be a future date")

        # 4 Normal process
        body = {
            "course_id":str(self.course.id),
            "from_date":"2025-07-20"
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertTrue(serializer.is_valid())

    def test_eol_api_course_serializers_passed(self):
        """
        test course serializers using different passed values
        1. Not null attribute
        2. Wrong format
        3. Normal process
        """
        # 1 Not null attribute
        body = {
            "course_id":str(self.course.id),
            "passed":None
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["passed"][0]), "This field may not be null.")

        # 2 wrong format
        body = {
            "course_id":str(self.course.id),
            "passed":"2027-07-20"
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["passed"][0]), "Must be a valid boolean.")

        # 3 Normal process
        body = {
            "course_id":str(self.course.id),
            "passed":True
        }
        serializer = StudentGradesSerializer(data=body)
        self.assertTrue(serializer.is_valid())

    def test_url_student_grades_with_anon_client(self):
        """
        test student_grades with anonymous client
        """
        data= {
            'course_id': str(self.course_2.id),
        }
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        self.assertEqual(response, {"detail": "Authentication credentials were not provided."})
        self.assertEqual(result.status_code, 401)

    def test_url_student_grades_with_no_permission(self):
        """
        test student_grades when user doesn't have access to this course_id
        """
        data= {
            'course_id': str(self.course_2.id),
        }
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        self.assertEqual(response, {"error": "You don't have permission"})
        self.assertEqual(result.status_code, 403)

    def test_url_student_grades_with_no_data(self):
        """
        test student_grades when no course_id wasn't sended
        """
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'))
        response = json.loads(result.content.decode('utf-8'))
        expected = {
            'course_id': ['This field is required.']
        }
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 400)

    def test_url_student_grades_with_no_student(self):
        """
        test student_grades with course_id and no student data
        """
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        data= {
            'course_id':str(self.course.id),
        }
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        expected = [{
            'course_data':{
                'cutoff':0.5,
                'display_name': '2022',
                'ucursos_id': None,
                'id_course':str(self.course.id)
                },
            'student_data':[]
        }]
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_student_grades_with_ucursos_id(self):
        """
        test student_grades with course_id and no student data
        but adding a ucurso_course map
        """
        data= {
            'course_id':str(self.course.id),
        }
        EdxUCursosMapping.objects.create(
            edx_course=self.course.id,
            ucurso_course="course/test/map"
        )
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        expected = [{
            'course_data':{
                'cutoff':0.5,
                'display_name': '2022',
                'ucursos_id': 'course/test/map',
                'id_course':str(self.course.id)
                },
            'student_data':[]
        }]
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_student_grades_with_students(self):
        """
        test student_grades with course_id, adding a ucurso_course map and adding student_data
        """
        # Create EdxUCursosMapping
        EdxUCursosMapping.objects.create(
            edx_course=self.course.id,
            ucurso_course="course/test/map"
        )
        now = datetime.datetime.now() 
        now_1 = now +datetime. timedelta(minutes=1)
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=10,
            grading_policy_hash='policy',
            percent_grade=0.8,
            letter_grade='Pass',
            passed_timestamp=now,
            modified=now
        )
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=12,
            grading_policy_hash='policy',
            percent_grade=0.4,
            letter_grade='',
            passed_timestamp=now_1,
            modified=now_1
        )
        data = {
            'course_id':str(self.course.id),
        }
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        expected = [{
            'course_data':{
                    'cutoff': 0.5,
                    'display_name': '2022',
                    'ucursos_id': 'course/test/map',
                    'id_course':str(self.course.id)
                },
            'student_data':[
                {
                    'document_id': None,
                    'passed_timestamp': now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'percent_grade': 0.8,
                    'grade': 5.8,
                    'modified': now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
        }]
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_student_grades_with_students_passed_False(self):
        """
        test student_grades with course_id, adding a ucurso_course map, adding student_data
        and passed as False, meaning all student in a course and its info must be returned
        """
        # Create EdxUCursosMapping
        EdxUCursosMapping.objects.create(
            edx_course=self.course.id,
            ucurso_course="course/test/map"
        )
        now = datetime.datetime.now()
        now_1 = now +datetime. timedelta(minutes=1)
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=10,
            grading_policy_hash='policy',
            percent_grade=0.8,
            letter_grade='Pass',
            passed_timestamp=now,
            modified=now
        )
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=12,
            grading_policy_hash='policy',
            percent_grade=0.4,
            letter_grade='',
            passed_timestamp=now_1,
            modified=now_1
        )
        data = {
            'course_id':str(self.course.id),
        }
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        expected = [{
            'course_data':{
                    'cutoff': 0.5,
                    'display_name': '2022',
                    'ucursos_id': 'course/test/map',
                    'id_course': str(self.course.id)
                },
            'student_data':[
                {    
                    'document_id': None,
                    'passed_timestamp': now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'percent_grade': 0.8,
                    'grade': 5.8,
                    'modified': now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                },
                {    
                    'document_id': None,
                    'passed_timestamp': now_1.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'percent_grade': 0.4,
                    'grade': 3.4,
                    'modified': now_1.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
        }]
        data = {
            'course_id': str(self.course.id),
            'passed': False
        }
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_student_grades_with_students_with_passed_True(self):
        """
        test student_grades with course_id, adding a ucurso_course map, adding student_data
        and passed as True, meaning only student who passed in a course and its info must be returned
        """
        data= {
            'course_id': str(self.course.id),
            'passed': True
        }
        EdxUCursosMapping.objects.create(
            edx_course=self.course.id,
            ucurso_course="course/test/map"
        )
        now = datetime.datetime.now()
        now_1 = now +datetime. timedelta(minutes=1)
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=10,
            grading_policy_hash='policy',
            percent_grade=0.8,
            letter_grade='Pass',
            passed_timestamp=now,
            modified=now
        )
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=12,
            grading_policy_hash='policy',
            percent_grade=0.4,
            letter_grade='',
            passed_timestamp=now_1,
            modified=now_1
        )
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        expected = [{
            'course_data':{
                    'cutoff': 0.5,
                    'display_name': '2022',
                    'ucursos_id': 'course/test/map',
                    'id_course':str(self.course.id)
                },
            'student_data':[
                {    
                    'document_id': None,
                    'passed_timestamp': now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'percent_grade': 0.8,
                    'grade': 5.8,
                    'modified': now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            ]
        }]
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_student_grades_with_students_with_from_date(self):
        """
        test student_grades with course_id, adding a ucurso_course map, adding student_data,
        passed as True and from_date, meaning only student who passes before an specific date in a course and its info must be returned
        """
        data= {
            'course_id': str(self.course.id),
            'passed': True,
            'from_date': '2025-07-20'
        }
        EdxUCursosMapping.objects.create(
            edx_course=self.course.id,
            ucurso_course="course/test/map"
        )
        date_after = datetime.datetime(2025, 7, 25, tzinfo=datetime.timezone.utc)
        date_before = datetime.datetime(2025, 7, 15, tzinfo=datetime.timezone.utc)
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=10,
            grading_policy_hash='policy',
            percent_grade=0.8,
            letter_grade='Pass',
            passed_timestamp=date_after,
            modified=date_after
        )
        PersistentCourseGrade.objects.create(
            course_id=self.course.id,
            user_id=12,
            grading_policy_hash='policy',
            percent_grade=0.4,
            letter_grade='',
            passed_timestamp=date_before,
            modified=date_before
        )
        self.client_token.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:student_grades'), data)
        response = json.loads(result.content.decode('utf-8'))
        expected = [{
            'course_data':{
                    'cutoff': 0.5,
                    'display_name': '2022',
                    'ucursos_id': 'course/test/map',
                    'id_course':str(self.course.id)
                },
            'student_data':[
                {    
                    'document_id': None,
                    'passed_timestamp': '2025-07-25T00:00:00Z',
                    'percent_grade': 0.8,
                    'grade': 5.8,
                    'modified': '2025-07-25T00:00:00Z',
                }
            ]
        }]
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_get_client_courses(self):
        """
        test get_client_courses normal process to obtain a list of courses_ids 
        """
        self.client_token.credentials(HTTP_AUTHORIZATION = 'Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:get_client_courses'))
        response = json.loads(result.content.decode('utf-8'))
        expected ={'courses_ids':[str(self.course.id), str(self.course_3.id)]}
        self.assertEqual(response, expected)
        self.assertEqual(result.status_code, 200)

    def test_url_get_client_courses_with_no_access_to_any_courses(self):
        """
        test get_client_courses when user doesn't have access to any courses
        """
        ClientCourseAccess.objects.filter(client=self.application).delete()
        self.client_token.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        result = self.client_token.get(reverse('eol_api:get_client_courses'))
        response = json.loads(result.content.decode('utf-8'))
        self.assertEqual(response, {"error": "You don't have access to any courses"})
        self.assertEqual(result.status_code, 403)
