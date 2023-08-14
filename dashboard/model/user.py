class User:
    def __init__(self, decoded_cookie: dict):
        self.username = decoded_cookie.get("preferred_username")
        self.full_name = decoded_cookie.get("name")
        names = self.full_name.split(" ")
        self.initials = names[0][0] + names[1][0] if len(names) > 1 else names[0][0]
        self.sub = decoded_cookie.get("sub")
        realm_access = decoded_cookie.get("realm_access")
        if realm_access is not None:
            self.roles = realm_access.get("roles")
        else:
            self.roles = []

    def __str__(self):
        return (f"Username: {self.username}\n"
                f"Fullname: {self.full_name}\n"
                f"Initials: {self.initials}\n"
                f"Roles: {self.roles}")



