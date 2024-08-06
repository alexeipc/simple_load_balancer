class BalancerInterface:
    def get_the_best_server(self) -> dict | None:
        """Get the most suitable server base on a specific criterial
        Returns:
            dict | None: the most suitable server
        """
        return {}
    def active(self, server: dict) -> None:
        """ Active the request to the given server
        Args:
            server (dict): the given server
        """
        pass
    def release(self, server: dict) -> None:
        """ Finish up the request to the given server
        Args:
            server (dict): the given server
        """
        pass