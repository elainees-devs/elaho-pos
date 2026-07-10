from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Role
from apps.users.models import User
class RoleService:
    """
    Service responsible for role management.

    Responsibilities:
    - Create roles
    - Update roles
    - Delete roles
    - Assign roles to users
    - Retrieve roles
    """
    @staticmethod
    @transaction.atomic
    def create_role(**data) -> Role:
        """
        Create a new role.
        """
        data["name"] = data["name"].strip()
        if Role.objects.filter(name=data["name"]).exists():
            raise ValidationError("Role already exists.")
        return Role.objects.create(**data)
    

    @staticmethod
    @transaction.atomic
    def update_role(role:Role, **data) ->Role:
        """
        Update an existing role.
        """
        for field, value in data.items():
            setattr(role, field, value)

        role.full_clean()
        role.save()
        return role

    @staticmethod
    def delete_role(role:Role) -> None:
        """
        Delete a role.
        """
        role.delete()

    @staticmethod
    @transaction.atomic
    def assign_role(user: User, role: Role) -> User:
        """
        Assign a role to a user.
        Assumes one role per user.
        """
        user.role = role
        user.save(update_fields=["role"])
        return user

    @staticmethod
    def get_role(role_id:int) -> Role:
        """
        Retrieve a role by its ID.
        """
        return Role.objects.get(pk=role_id)

    @staticmethod
    def list_roles():
        """
        Return all roles.
        """
        return Role.objects.all()
  