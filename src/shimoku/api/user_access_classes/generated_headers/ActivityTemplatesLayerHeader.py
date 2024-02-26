# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional


class ActivityTemplatesLayerHeader:
    """
    This class is used to interact with the API at the activity template metadata level.
    """

    def get_activity_template(
        self,
        uuid: Optional[str] = None,
        name_version: Optional[tuple[str, str]] = None,
    ) -> dict:
        """Get a workspace
        :param name_version: name and version of the activity template
        :param uuid: UUID of the activity template
        """
        pass
