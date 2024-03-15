import json
from typing import Any


def get_appsettings() -> dict[str, tuple]:
    with open('static/appsettings.json', 'r') as file:
        data: dict = json.load(file)
        
        roles: tuple = tuple(data['Settings']['priv_roles'])
        
        #appsettings: dict[str, Any] = {'roles': [role for role in data["Settings"]['priv_roles']]}
        appsettings: dict[str, tuple] = {'roles': roles}
        
        return appsettings