import os

from auth0.v3.management import Auth0
from auth0.v3.authentication import GetToken


def create_client(jupyterhub_endpoint, project_name):
    for variable in {'AUTH0_DOMAIN', 'AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET'}:
        if variable not in os.environ:
            raise ValueError(f'Required environment variable={variable} not defined')

    get_token = GetToken(os.environ["AUTH0_DOMAIN"])
    token = get_token.client_credentials(
        os.environ['AUTH0_CLIENT_ID'],
        os.environ['AUTH0_CLIENT_SECRET'],
        f'https://{os.environ["AUTH0_DOMAIN"]}/api/v2/'
    )
    mgmt_api_token = token["access_token"]

    auth0 = Auth0(os.environ["AUTH0_DOMAIN"], mgmt_api_token)

    credentials = auth0.clients.create(
        {
            "name": f"{project_name}",
            "description": f"QHub - {project_name} - {jupyterhub_endpoint}",
            "callbacks": [f"https://{jupyterhub_endpoint}/hub/oauth_callback"],
            "app_type": "regular_web",
        }
    )

    return {
        "auth0_subdomain": ".".join(os.environ["AUTH0_DOMAIN"].split(".")[:-2]),
        "client_id": credentials["client_id"],
        "client_secret": credentials["client_secret"],
        "scope": ["openid", "email", "profile"],
        "oauth_callback_url": f"https://{jupyterhub_endpoint}/hub/oauth_callback",
    }
