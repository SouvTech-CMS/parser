from loguru import logger
from configs import settings

logger.add(
	settings.LOG_FILE,
	format="{time} {level} {message}",
	level="DEBUG",
	rotation="100 MB",
	compression="zip",
	serialize=True,
)


__all__ = ["logger"]
