from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command, CommandError


class Command(BaseCommand):
    help = "Set up a 30-day trial configuration and optionally load demo data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-date",
            default=None,
            help="Trial start date in ISO format (YYYY-MM-DD). Defaults to today.",
        )
        parser.add_argument(
            "--duration-days",
            type=int,
            default=30,
            help="Trial duration in days. Defaults to 30.",
        )
        parser.add_argument(
            "--fixture",
            default=getattr(settings, "TRIAL_DEMO_DATA_FIXTURE", "django_data.json"),
            help="Fixture file to load as demo data.",
        )
        parser.add_argument(
            "--skip-demo-data",
            action="store_true",
            help="Skip loading demo data fixture.",
        )

    def handle(self, *args, **options):
        duration_days = options["duration_days"]
        if duration_days <= 0:
            raise CommandError("duration-days must be greater than 0")

        if options["start_date"]:
            start_date = date.fromisoformat(options["start_date"])
        else:
            start_date = date.today()

        end_date = start_date + timedelta(days=duration_days)

        if not options["skip_demo_data"]:
            fixture_path = Path(options["fixture"])
            if not fixture_path.exists():
                raise CommandError(f"Fixture not found: {fixture_path}")
            call_command("loaddata", str(fixture_path))
            self.stdout.write(self.style.SUCCESS(f"Loaded demo data: {fixture_path}"))

        trial_env_file = Path(".env.trial")
        trial_env_file.write_text(
            "\n".join(
                [
                    "TRIAL_MODE=True",
                    f"TRIAL_START_DATE={start_date.isoformat()}",
                    f"TRIAL_DURATION_DAYS={duration_days}",
                    f"TRIAL_END_DATE={end_date.isoformat()}",
                    f"TRIAL_DEMO_DATA_FIXTURE={options['fixture']}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        self.stdout.write(self.style.SUCCESS("Trial configuration created: .env.trial"))
        self.stdout.write(
            self.style.WARNING(
                "Add these values to your .env file to enable runtime trial enforcement."
            )
        )
