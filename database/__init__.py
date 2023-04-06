from enum import Enum
from database import Teachers, Schedule

name = "SUAIBot"


class CollectionNames(Enum):
    USERS = "Users"
    SCHEDULE = "Schedule"
    TEACHERS = "Teachers"
