from src.app.domain.services.piston_service import PistonService


def get_piston_service() -> PistonService:
    """
    Provide piston service instance.

    :return: piston service
    """
    return PistonService()
