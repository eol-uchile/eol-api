# Python Standard Libraries
import datetime
import logging

# Installed packages (via pip)
from rest_framework import serializers

# Edx dependencie
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


def validate_course(id_course):
    """
    Verify if course.id exists
    """
    try:
        aux = CourseKey.from_string(id_course)
        return CourseOverview.objects.filter(id=aux).exists()
    except InvalidKeyError:
        logger.error("eol-Api error validate course, invalid format: {}".format(id_course))
        return False

logger = logging.getLogger(__name__)

class StudentGradesSerializer(serializers.Serializer):
    """
    This serializer allows to check incoming query params
    
    """
    course_id = serializers.CharField(required=True, allow_blank=False)
    from_date = serializers.DateField(
        required=False, 
        input_formats=['%d-%m-%Y', '%d-%m-%Y %H:%M', '%d-%m-%Y %H:%M:%S']
        )
    passed = serializers.BooleanField(required=False, default=True)

    def validate_course_id(self, value):
        course_id = value
        if not validate_course(course_id):
            logger.error('StudentGradesSerializer - Course key not valid or dont exists: {}'.format(course_id))
            raise serializers.ValidationError(u"Course key not valid or dont exists: {}".format(course_id))
        return course_id

    def validate_from_date(self, value):
        if value > datetime.date.today():
            logger.error('StudentGradesSerializer - from_date can´t be a future date {}'.format(value))
            raise serializers.ValidationError("from_date can´t be a future date")
        return value
    
    def validate_passed(self, value):
        return value
