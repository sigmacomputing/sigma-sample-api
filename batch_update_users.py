#!/usr/bin/env python3

import argparse
import requests
import csv

def get_baseurl(env):
    if env == 'production':
        return "https://aws-api.sigmacomputing.com"
    else:
        return "https://api.staging.sigmacomputing.io"

def get_access_token(env, client_id, client_secret):
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
    base_url = get_baseurl(env)
    response = requests.post(f"{base_url}/v2/auth/token", data=payload)
    print(response)
    data = response.json()

    return data["access_token"]


def get_headers(access_token):
    """ Gets headers for API requests

        :access_token:  Generated access token
        :returns:       Headers for API requests

    """
    return {"Authorization": "Bearer " + access_token}



def update_member(env, access_token, user_id, payload):
    """ Update member

        :access_token:  Generated access token
        :userId:        ID of the user to update
        :payload:       Fields to update

        :returns:       Member ID

    """
    base_url = get_baseurl(env)
    response = requests.patch(
        f"{base_url}/v2/members/{user_id}",
        headers=get_headers(access_token),
        json=payload
    )
    data = response.json()
    return data["memberId"]

def get_all_members(env, access_token):
    base_url = get_baseurl(env)
    response = requests.get(
        f'{base_url}/v2/members',
        headers=get_headers(access_token)
    )
    res = response.json()
    return res

def main():
    parser = argparse.ArgumentParser(
        description='Batch update organization member by email')

    parser.add_argument(
        '--client_id', type=str, required=True, help='Client ID generated from Sigma')
    parser.add_argument(
        '--client_secret', type=str, required=True, help='Client secret generated from Sigma')
    parser.add_argument(
        '--csv', type=str, required=True, help='CSV file containing all the data, format expected: Email,First Name,Last Name,New Email')
    parser.add_argument(
        '--env', type=str, required=True, help='env to use: [production | staging].'
    )
    args = parser.parse_args()
    access_token = get_access_token(args.env, args.client_id, args.client_secret)
    # parse csv
    updated_members = []
    with open(args.csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            updated_members.append(row)

    # Get all members for the organization
    members = get_all_members(args.env, access_token)

    members_dict = {}
    for m in members:
     members_dict[m['email']] = m['memberId']

    for m in updated_members:
        member_email = m['Email']
        member_id = members_dict[member_email]
        payload = {}
        for k, v in m.items():
            if k == 'First Name':
                payload['firstName'] = v
            if k == 'Last Name':
                payload['lastName'] = v
            if k == 'New Email':
                payload['email'] = v
        update_member(args.env, access_token, member_id, payload)


if __name__ == '__main__':
    main()
