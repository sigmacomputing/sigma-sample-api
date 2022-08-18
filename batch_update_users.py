#!/usr/bin/env python3

import argparse
import requests
import csv

def get_baseurl(env, cloud):
    if env == 'production':
        if cloud == 'aws':
            return "https://aws-api.sigmacomputing.com"
        elif cloud == 'gcp':
            return "https://api.sigmacomputing.com"
    elif env == 'staging':
        if cloud == 'aws':
            return "https://staging-aws-api.sigmacomputing.io"
        elif cloud == 'gcp':
            return "https://api.staging.sigmacomputing.io"

    raise Exception(f"Unknown env/cloud: {env}/{cloud}")

def get_access_token(url, client_id, client_secret):
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
    response = requests.post(f"{url}/v2/auth/token", data=payload)
    print(f"Get Access Token response: {response}")
    data = response.json()

    return data["access_token"]


def get_headers(access_token):
    """ Gets headers for API requests

        :access_token:  Generated access token
        :returns:       Headers for API requests

    """
    return {"Authorization": "Bearer " + access_token}



def update_member(url, access_token, user_id, payload):
    """ Update member

        :access_token:  Generated access token
        :userId:        ID of the user to update
        :payload:       Fields to update

        :returns:       Member ID

    """
    response = requests.patch(
        f"{url}/v2/members/{user_id}",
        headers=get_headers(access_token),
        json=payload
    )
    data = response.json()
    return data["memberId"]

def get_all_members(url, access_token):
    response = requests.get(
        f'{url}/v2/members',
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
    parser.add_argument(
        '--cloud', type=str, required=True, help='cloud to use: [aws | gcp].'
    )
    parser.add_argument(
        '--skip_invalid_emails', type=str, required=False, help='should invalid emails be skipped: [yes]'
    )

    args = parser.parse_args()
    url = get_baseurl(args.env, args.cloud)
    access_token = get_access_token(url, args.client_id, args.client_secret)
    # parse csv
    updated_members = []
    with open(args.csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            updated_members.append(row)

    # Get all members for the organization
    members = get_all_members(url, access_token)

    members_dict = {}
    for m in members:
     members_dict[m['email']] = m['memberId']

    # when user enables skip_invalid_emails arg: script will bypass KeyErrors and try the next member_email in the updated_members list
    if args.skip_invalid_emails == "yes":

        for m in updated_members:
            member_email = m['Email']
            try:
                member_id = members_dict[member_email]
            except KeyError:
                print(f"\u2717 FAILURE! Did not update {member_email}: address not found or is for a deactivated account")
            else:
                payload = {}
                for k, v in m.items():
                    if k == 'First Name':
                        payload['firstName'] = v
                    if k == 'Last Name':
                        payload['lastName'] = v
                    if k == 'New Email':
                        payload['email'] = v
                try:
                    update_member(url, access_token, member_id, payload)
                except KeyError:
                    print(f"\u2717 FAILURE! Did not update {member_email}: {payload['email']} already in use")
                else:
                    print(f"\u2713 SUCCESS! {member_email} updated to {payload['email']}")

    # when user does not enable skip_invalid_emails arg: default script behavior when encountering KeyError is to abort (exit code 1)
    else:

        for m in updated_members:
            member_email = m['Email']
            try:
                member_id = members_dict[member_email]
            except KeyError:
                print(f"\u2717 FAILURE! Did not update {member_email}: address not found or is for a deactivated account")
                raise SystemExit("Script aborted")
            else:
                payload = {}
                for k, v in m.items():
                    if k == 'First Name':
                        payload['firstName'] = v
                    if k == 'Last Name':
                        payload['lastName'] = v
                    if k == 'New Email':
                        payload['email'] = v
                try:
                    update_member(url, access_token, member_id, payload)
                except KeyError:
                    print(f"\u2717 FAILURE! Did not update {member_email}: {payload['email']} already in use")
                    raise SystemExit("Script aborted")
                else:
                    print(f"\u2713 SUCCESS! {member_email} updated to {payload['email']}")


if __name__ == '__main__':
    main()
