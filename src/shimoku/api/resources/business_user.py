from typing import Optional, TYPE_CHECKING
from shimoku.api.base_resource import Resource
from dataclasses import dataclass

if TYPE_CHECKING:
    from .business import Business

import logging

logger = logging.getLogger(__name__)


class BusinessInvitation(Resource):
    """BusinessInvitation resource class"""

    resource_type = "user/invitation"
    url_post_name = "user/invite"
    plural = "user/invitations"
    alias_field = "email"

    def __init__(
        self,
        parent: "Business",
        uuid: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = dict(
            email="",
            roles=[],
            sendEmail=True,
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            check_params_before_creation=["email"],
            params=params,
        )

    async def delete(self) -> bool:
        return await self._base_resource.delete()


class BusinessUser(Resource):
    """BusinessUser resource class"""

    resource_type = "user"
    plural = "users"
    alias_field = "email"

    def __init__(
        self,
        parent: "Business",
        uuid: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = dict(
            id="",
            email="",
            name="",
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            # check_params_before_creation=["name"], Cant create this, Account is created by the system
            params=params,
        )

    async def delete(self) -> bool:
        return await self._base_resource.delete()
