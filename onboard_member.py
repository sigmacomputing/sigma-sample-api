#!/usr/bin/env python3

import argparse
import requests

BASE_URL = "https://aws-api.sigmacomputing.com"


def get_access_token(client_id, client_secret):
    """ Gets the access token from Sigma

        :client_id:     Client ID generated from Sigma
        :client_secret: Client secret generated from Sigma

        :returns:       Access token

    """
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(f"{BASE_URL}/v2/auth/token", data=payload)
    data = response.json()

    return data["access_token"]


def get_headers(access_token):
    """ Gets headers for API requests

        :access_token:  Generated access token
        :returns:       Headers for API requests

    """
    return {"Authorization": "Bearer " + access_token}


def create_member(access_token, email, first_name, last_name, member_type):
    """ Creates new organization member

        :access_token:  Generated access token
        :email:         Generated access token
        :first_name:    First name of the new member
        :last_name:     First name of the new member
        :member_type:   Member type of the new member

        :returns:       Information of newly created member

    """
    payload = {
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "memberType": member_type,
        "isGuest": False
    }
    response = requests.post(
        f"{BASE_URL}/v2/members",
        headers=get_headers(access_token),
        json=payload
    )
    data = response.json()
    return data["memberId"]


def grant_connection(access_token, connection_id, permission, member_id):
    """ Grants connection permission to a member

        :access_token:   Generated access token
        :connection_id:  ID of connection
        :permission:     Permission to be granted
        :member_id:      ID of the member to be granted permission

    """
    payload = {
        "grants": [
            {
                "grantee": {"memberId": member_id},
                "permission": permission
            }
        ]
    }
    requests.post(
        f"{BASE_URL}/v2/connections/{connection_id}/grants",
        headers=get_headers(access_token),
        json=payload
    )


def grant_workspace(access_token, workspace_id, permission, member_id):
    """ Grants workspace permission to a member

        :access_token:  Generated access token
        :workspace_id:  ID of workspace
        :permission:    Permission to be granted
        :member_id:     ID of the member to be granted permission

    """
    payload = {
        "grants": [
            {
                "grantee": {"memberId": member_id},
                "permission": permission
            }
        ]
    }
    requests.post(
        f"{BASE_URL}/v2/workspaces/{workspace_id}/grants", headers=get_headers(access_token), json=payload)


def main():
    parser = argparse.ArgumentParser(
        description='Onboard a new organization member')

    parser.add_argument(
        '--client_id', type=str, required=True, help='Client ID generated from Sigma')
    parser.add_argument(
        '--client_secret', type=str, required=True, help='Client secret generated from Sigma')
    parser.add_argument(
        '--email', type=str, required=True, help='Email of new member to be created')
    parser.add_argument(
        '--first_name', type=str, required=True, help='First name of new member to be created')
    parser.add_argument(
        '--last_name', type=str, required=True, help='Last name of new member to be created')
    parser.add_argument(
        '--member_type', type=str, required=True, help='Email of new member to be created')
    parser.add_argument(
        '--connection_id', type=str, help='Optional ID of connection to grant permission')
    parser.add_argument(
        '--workspace_id', type=str, help='Optional ID of workspace to grant permission')

    args = parser.parse_args()

    access_token = get_access_token(args.client_id, args.client_secret)

    # Create new organization member
    member_id = create_member(access_token, args.email,
                              args.first_name, args.last_name, args.member_type)

    # Assign the member to a connection
    if args.connection_id:
        connection_permission_map = {
            'creator': 'annotate', 'explorer': 'usage'}
        permission = connection_permission_map[args.member_type]
        grant_connection(access_token, args.connection_id,
                         permission, member_id)
    # Assign the member to a workspace
    elif args.workspace_id:
        workspace_permission_map = {
            'admin': 'edit', 'creator': 'organize', 'explorer': 'explore', 'viewer': 'view'}
        permission = workspace_permission_map[args.member_type]
        grant_workspace(access_token, args.workspace_id, permission, member_id)


if __name__ == '__main__':
    main()
