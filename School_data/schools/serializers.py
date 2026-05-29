from rest_framework import serializers
from .models import SchoolLevel, AcademicYear, Term, Classroom

class SchoolLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolLevel
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class TermSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model = Term
        fields = '__all__'

class ClassroomSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.get_name_display', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model = Classroom
        fields = '__all__'
