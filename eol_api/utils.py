# Python Standard Libraries
import decimal
import logging

# Installed packages (via pip)
from django.db.models import Q
from edxucursos.models import EdxUCursosMapping
from eol_sso.services.interface import get_indiv_id

# Edx dependencies
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.grades.models import PersistentCourseGrade
from opaque_keys.edx.keys import CourseKey

context = decimal.getcontext()
context.rounding = decimal.ROUND_HALF_UP

logger = logging.getLogger(__name__)

def grade_percent_scaled(grade_percent, grade_cutoff, min_grade=3, max_grade=7, decimal_digits=1):
    """
    Calculate chilean grade from a cutoff and a percentage
    """
    if grade_percent < grade_cutoff:
        raw_grade = float(min_grade) / grade_cutoff * grade_percent + 1.
    else:
        raw_grade = float(min_grade) / (1. - grade_cutoff) * grade_percent + (float(max_grade) - (float(min_grade) / (1. - grade_cutoff)))
    return round(decimal.Decimal(str(raw_grade)), decimal_digits)

def student_grades(course_id, from_date, passed = True):
    """
    Respond a summary of all students and its data from an specific course.
    """
    # course data
    course_key = CourseKey.from_string(course_id)
    course = get_course_by_id(course_key)
    grade_cutoff = min(course.grade_cutoffs.values())
    ucursos_id = EdxUCursosMapping.objects.filter(edx_course=course_id).values_list('ucurso_course', flat=True).first()
    display_name = course.display_name
    
    # student data
    query = Q(course_id=course_id)
    if passed:
        query &= Q(letter_grade__isnull=False) & ~Q(letter_grade='')
        if from_date:
            query &= Q(passed_timestamp__gte=from_date)

    persistent_grades_users = PersistentCourseGrade.objects.filter(query).values_list('user_id','percent_grade','passed_timestamp','letter_grade')
    student_data = []
    for grade in persistent_grades_users:
        percent_grade = grade[1]
        student_data.append({
            'document_id':get_indiv_id(grade[0]),
            'passed_timestamp': grade[2],
            'percent_grade': percent_grade,
            'grade': grade_percent_scaled(percent_grade, grade_cutoff)
        })

    response_payload =[{
        'course_data':{
            'cutoff':grade_cutoff,
            'display_name': display_name,
            'ucursos_id': ucursos_id,
            'id_course':course_id
            },
        'student_data':student_data
    }]
    
    return response_payload
