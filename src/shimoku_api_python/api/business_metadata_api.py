""""""


class BusinessMetadataApi(object):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def copy_business(self):
        """Having a business make a copy of all its apps and reports
        for a new business (without data) so that the data could be filled next
        """
        raise NotImplementedError