# Python Standard Libraries
import logging

# Installed packages (via pip)
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

# Edx dependencies
from openedx.core.lib.api.authentication import BearerAuthentication

# Internal project dependencies
from .models import ClientCourseAccess
from .serializers import StudentPerCourseSerializer
from .utils import get_student_per_course

logger = logging.getLogger(__name__)

class CustomUserRateThrottle(UserRateThrottle):
    """
    This is a custom rate throttle this overwrite default throttle values
    """
    def get_rate(self):
        return getattr(settings, 'EOL_API_RATE', '1/minute')

class StudentPerCourse(APIView):
    """
    To use this API you must be logged and have access in ClientCourseAccess
    Return a list of course data and student data in this format:
    [{
        'course_data':{
                'cutoff':0.5,
                'display_name': '2022',
                'ucursos_id': 'course/test/map',
                'id_course':'course/test/123'
            },
        'student_data':[
            {    
                'document_id':11111111-1,
                'passed_timestamp': 2025-07-25T00:00:00Z,
                'percent_grade': 0.8,
                'grade': 5.8
            },
            {    
                'document_id':22222222-2,
                'passed_timestamp': 2025-07-15T00:00:00Z,
                'percent_grade': 0.4,
                'grade': 3.4
            }
        ]
    }]
    """
    authentication_classes = (BearerAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = [CustomUserRateThrottle]
    
    def get(self, request, format=None):
        serializer = StudentPerCourseSerializer(data=request.query_params)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            token = request.auth
            application = token.application
            has_access = ClientCourseAccess.objects.filter(
                client = application,
                course_id = course_id
            ).exists()
            if has_access:
                from_date = serializer.validated_data.get('from_date') 
                passed = serializer.validated_data.get('passed') 
                response = get_student_per_course(course_id, from_date, passed)
                return Response(data=response, status=status.HTTP_200_OK)
            else:
                logger.error("EOL-API - StudentPerCourse - You don't have permission")
                return Response({"error": "You don't have permission"}, status=status.HTTP_403_FORBIDDEN)
        else:
            logger.error("EOL-API - StudentPerCourse - serializer is not valid")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        