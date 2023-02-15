from pathlib import Path

settings_dir = Path(__file__).parent
default_settings_file = str(Path(settings_dir, "default_settings.toml").absolute())
user_settings_file = str(Path(settings_dir, "user_settings.toml"))
dotenv_settings_file = str(Path(settings_dir, ".env").absolute())

# from .manager import settings
