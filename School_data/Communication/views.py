from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin from django.db.models import Q
from django.urls import reverse_lazy

from users.mixins import RoleRequiredMixin
from .models import Announcement, Message

# --- Announcements ---

class AnnouncementListView(LoginRequiredMixin, ListView):
    """
    Allows any logged-in user (all roles) to see announcements relevant to them.
    """
    model = Announcement
    template_name = 'communication/announcement_list.html'
    context_object_name = 'announcements'
    
    def get_queryset(self):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'profile'):
            return Announcement.objects.none()

        user = self.request.user
        role = user.profile.role
        
        # Base query for active announcements
        active_announcements = Announcement.objects.filter(is_active=True)
        
        # Build a query with all relevant scopes for the user
        # Announcements can be GLOBAL or targeted at the user's specific ROLE
        relevant_scopes = Q(scope='GLOBAL') | Q(scope=role)
        
        # If the user is a student or parent, also include announcements for their class
        if role in ['STUDENT', 'PARENT'] and user.profile.related_student:
            student = user.profile.related_student
            if student.current_class:
                relevant_scopes |= Q(scope='CLASS', target_class=student.current_class)

        # Order by newest first and remove duplicates
        return active_announcements.filter(relevant_scopes).order_by('-created_at').distinct()

class AnnouncementCreateView(RoleRequiredMixin, CreateView):
    """
    Only Admins and Headteachers can create new announcements.
    """
    allowed_roles = ['ADMIN', 'HEAD']
    model = Announcement
    fields = ['title', 'content', 'scope', 'target_class', 'is_active']
    template_name = 'communication/announcement_create.html'
    success_url = reverse_lazy('announcement_list')
    
    def form_valid(self, form):
        # Automatically set the poster to the current user
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

# --- Messaging ---

class MessageInboxView(LoginRequiredMixin, ListView):
    """
    Displays messages received by the current user.
    """
    model = Message
    template_name = 'communication/inbox.html'
    context_object_name = 'messages'
    
    def get_queryset(self):
        # Fetch messages where the current user is the receiver
        return Message.objects.filter(receiver=self.request.user).order_by('-sent_at')

class MessageDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a single message.
    """
    model = Message
    template_name = 'communication/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        # Ensure the user can only view messages they sent or received
        return Message.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark message as read when viewed, if the user is the receiver
        if obj.receiver == self.request.user and not obj.is_read:
            obj.is_read = True
            obj.save()
        return obj
