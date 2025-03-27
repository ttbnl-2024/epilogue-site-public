#!/usr/bin/env -S uv run
import os
import sys

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gph.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions.
        try:
            import django  # noqa: F401
        except ImportError as e:
            msg = (
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
            raise ImportError(msg) from e
        raise
    execute_from_command_line(sys.argv)
