import factory
from django.contrib.auth import get_user_model

from apps.roles.models import Role, Permission, RolePermission


User = get_user_model()


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f"Role {n}")
    level = 0
    description = ""


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission

    name = factory.Sequence(lambda n: f"Permission {n}")
    code = factory.Sequence(lambda n: f"test.code.{n}")
    description = ""


class RolePermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RolePermission

    role = factory.SubFactory(RoleFactory)
    permission = factory.SubFactory(PermissionFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = ""
    is_active = True
    role = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "password123")
        instance = model_class(*args, **kwargs)
        instance.set_password(password)
        instance.save()
        return instance
