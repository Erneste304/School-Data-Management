from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, DocumentCategory
from .serializers import DocumentSerializer, DocumentCategorySerializer


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Document.objects.select_related('uploaded_by', 'category').all()
        user = self.request.user
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        # Non-admin users only see public docs or their own uploads
        if user.role not in ('admin', 'head_teacher'):
            qs = qs.filter(is_public=True) | qs.filter(uploaded_by=user)

        if category:
            qs = qs.filter(category_id=category)
        if search:
            qs = qs.filter(title__icontains=search)

        return qs.distinct()

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        file_size = uploaded_file.size if uploaded_file else 0
        file_type = uploaded_file.content_type if uploaded_file else ''
        serializer.save(
            uploaded_by=self.request.user,
            file_size=file_size,
            file_type=file_type
        )

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        doc = self.get_object()
        doc.increment_download_count()
        return Response({'file_url': doc.file.url, 'downloads': doc.download_count})
