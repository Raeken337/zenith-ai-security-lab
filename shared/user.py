class User:
    def __init__(
        self,
        username,
        full_name,
        department,
        groups,
        role,
        work_start,
        work_end
    ):
        self.username = username
        self.full_name = full_name
        self.department = department
        self.groups = groups
        self.role = role
        self.work_start = work_start
        self.work_end = work_end

    def get_profile(self):
        return {
            "username": self.username,
            "full_name": self.full_name,
            "department": self.department,
            "groups": self.groups,
            "role": self.role,
            "work_start": self.work_start,
            "work_end": self.work_end
        }