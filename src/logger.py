from enum import StrEnum

from loguru import logger


class Instance(StrEnum):
    ONE = "instance-1"
    TWO = "instance-2"


logger.level(Instance.ONE, no=38, color="<yellow>", icon="1️⃣")
logger.level(Instance.TWO, no=38, color="<magenta>", icon="2️⃣")
logger.level("cli", no=38, color="<green>", icon="⚙")
