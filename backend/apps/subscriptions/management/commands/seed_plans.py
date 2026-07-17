from django.core.management.base import BaseCommand

from apps.subscriptions.models import SubscriptionPlan


DEFAULT_PLANS = [
    {
        "name": "Starter",
        "slug": "starter",
        "description": "For small businesses just getting started.",
        "monthly_price": 1500,
        "annual_price": 15000,
        "max_users": 3,
        "max_branches": 1,
        "max_products": 200,
    },
    {
        "name": "Standard",
        "slug": "standard",
        "description": "For growing businesses with multiple staff.",
        "monthly_price": 3500,
        "annual_price": 35000,
        "max_users": 10,
        "max_branches": 3,
        "max_products": 1000,
    },
    {
        "name": "Premium",
        "slug": "premium",
        "description": "For established businesses with advanced needs.",
        "monthly_price": 7000,
        "annual_price": 70000,
        "max_users": 25,
        "max_branches": 10,
        "max_products": 5000,
    },
    {
        "name": "Enterprise",
        "slug": "enterprise",
        "description": "For large operations with unlimited access.",
        "monthly_price": 15000,
        "annual_price": 150000,
        "max_users": 100,
        "max_branches": 50,
        "max_products": 50000,
    },
]


class Command(BaseCommand):
    help = "Seed the database with default subscription plans."

    def handle(self, *args, **options):
        self.stdout.write("Seeding subscription plans...")

        for plan_data in DEFAULT_PLANS:
            plan, created = SubscriptionPlan.objects.get_or_create(
                slug=plan_data["slug"],
                defaults=plan_data,
            )
            if created:
                self.stdout.write(
                    f"  Plan '{plan.name}' created "
                    f"(KES {plan.monthly_price}/mo, KES {plan.annual_price}/yr)"
                )
            else:
                self.stdout.write(f"  Plan '{plan.name}' already exists")

        self.stdout.write(self.style.SUCCESS("Done."))
