class Endpoint:
    def __init__(
        self,
        device_id,
        device_type,
        assigned_user,
        site,
        connection_type
    ):
        self.device_id = device_id
        self.device_type = device_type
        self.assigned_user = assigned_user
        self.site = site
        self.connection_type = connection_type

    def get_profile(self):
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "assigned_user": self.assigned_user,
            "site": self.site,
            "connection_type": self.connection_type
        }