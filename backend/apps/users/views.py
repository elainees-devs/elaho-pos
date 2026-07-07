from rest_framework import viewsets

from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
ViewSet for managing User resources.

Provides the following REST API operations:

- GET    /users/          List all users
- GET    /users/{id}/     Retrieve a specific user
- POST   /users/          Create a new user
- PUT    /users/{id}/     Replace an existing user details
- PATCH  /users/{id}/     Partially update user details
- DELETE /users/{id}/     Delete a user
"""
    queryset = User.objects.all()
    serialize_class = UserSerializer