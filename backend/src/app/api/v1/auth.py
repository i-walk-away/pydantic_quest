from fastapi import APIRouter, Depends

from src.app.core.dependencies.services.auth import get_auth_service
from src.app.domain.models.dto.auth import LoginCredentials, LoginResponse
from src.app.domain.services import AuthService

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(path='/login', summary='login')
async def login(
        credentials: LoginCredentials,
        auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """
    # Mardkdown docstring
    This is a test to see how SwaggerUI handles markdown dosctring formatting.

    ## Args
    `codeblock` -  description \n
    `cia` - argument description \n
    """
    jwt_token = await auth_service.login(credentials=credentials)

    return LoginResponse(access_token=jwt_token)
