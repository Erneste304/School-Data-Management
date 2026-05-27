from rest_framework import viewsets, permissions
from .models import AlumniProfile, AlumniEvent, AlumniJobPosting, AlumniDonation
from .serializers import (
    AlumniProfileSerializer, AlumniEventSerializer,
    AlumniJobPostingSerializer, AlumniDonationSerializer
)


class AlumniProfileViewSet(viewsets.ModelViewSet):
    queryset = AlumniProfile.objects.select_related('user').all()
    serializer_class = AlumniProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlumniEventViewSet(viewsets.ModelViewSet):
    queryset = AlumniEvent.objects.all().order_by('-event_date')
    serializer_class = AlumniEventSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlumniJobPostingViewSet(viewsets.ModelViewSet):
    queryset = AlumniJobPosting.objects.filter(is_active=True).order_by('-posted_date')
    serializer_class = AlumniJobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Requires alumni profile
        try:
            profile = AlumniProfile.objects.get(user=self.request.user)
            serializer.save(posted_by=profile)
        except AlumniProfile.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You must have an alumni profile to post jobs.')


class AlumniDonationViewSet(viewsets.ModelViewSet):
    queryset = AlumniDonation.objects.all().order_by('-donation_date')
    serializer_class = AlumniDonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role not in ('admin', 'head_teacher'):
            try:
                profile = AlumniProfile.objects.get(user=self.request.user)
                qs = qs.filter(alumni=profile)
            except AlumniProfile.DoesNotExist:
                qs = qs.none()
        return qs
