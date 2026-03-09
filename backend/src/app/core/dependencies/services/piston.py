from src.app.domain.services.code_runner import CodeRunner
from src.app.domain.services.piston_service import PistonService


def get_piston_service() -> CodeRunner:
    """
    Provide piston service instance.

    :return: piston service
    """

    return PistonService()
