from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SchoolLevel, AcademicYear, Term, Classroom
from .serializers import SchoolLevelSerializer, AcademicYearSerializer, TermSerializer, ClassroomSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def level_list(request):
    levels = SchoolLevel.objects.all()
    serializer = SchoolLevelSerializer(levels, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def academic_year_list(request):
    years = AcademicYear.objects.all()
    serializer = AcademicYearSerializer(years, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def term_list(request):
    terms = Term.objects.all()
    serializer = TermSerializer(terms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def classroom_list(request):
    classrooms = Classroom.objects.all()
    serializer = ClassroomSerializer(classrooms, many=True)
    return Response(serializer.data)
