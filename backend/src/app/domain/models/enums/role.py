from enum import Enum


class UserRole(str, Enum):
    """
    User role definition.
    """

    ADMIN = "admin"
    USER = "user"
