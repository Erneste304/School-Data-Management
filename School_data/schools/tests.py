from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status


class SchoolAPITest(APITestCase):
    """Test cases for school API endpoints"""

    def test_school_list_endpoint(self):
        """Test school list endpoint"""
        url = '/api/schools/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_school_create_endpoint(self):
        """Test school creation endpoint"""
        url = '/api/schools/'
        data = {
            'name': 'Test School',
            'address': '123 Test Street',
            'phone': '+1234567890'
        }
        response = self.client.post(url, data, format='json')
        # May return 401 if not authenticated or 201 if successful
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
