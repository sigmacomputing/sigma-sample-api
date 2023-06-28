#!/usr/bin/env python3

import argparse
import csv

import requests

from utils import SigmaClient

def update_member(client, user_id, payload):
    """ Update member

        :access_token:  Generated access token
        :userId:        ID of the user to update
        :payload:       Fields to update

        :returns:       Response JSON

    """
    try:
        response = client.patch(
            f"v2/members/{user_id}",
            json=payload
        )
        response.raise_for_status()
    # HTTP and other errors are handled generally by raising them as exceptions to be surfaced in downstream code
    except requests.exceptions.HTTPError as errh:
        # The API response's message value is sent in lieu of the full response to display to the user for clarity
        # Certain error response messages are useful for the user troubleshoot common issues, such as invalid Member Type or New Email already in use
        raise Exception(errh.response.status_code, f"API message: {errh.response.json()['message']}")
    except requests.exceptions.ConnectionError as errc:
        raise Exception(f"Connection Error: {errc}, API response: {errc.response.text}")
    except requests.exceptions.Timeout as errt:
        raise Exception(f"Timeout Error: {errt}, API response: {errt.response.text}")
    except requests.exceptions.RequestException as err:
        raise Exception(f"Other Error: {err}, API response: {err.response.text}")
    else:
        data = response.json()

        return data


def get_all_members(client):
    try:
        response = client.get(
            'v2/members?includeArchived=true'
        )
        response.raise_for_status()
 
    except requests.exceptions.HTTPError as errh:
        raise Exception(f"Connection Error: {errh}, API response: {errh.response.text}")
    except requests.exceptions.ConnectionError as errc:
        raise Exception(f"Connection Error: {errc}, API response: {errc.response.text}")
    except requests.exceptions.Timeout as errt:
        raise Exception(f"Timeout Error: {errt}, API response: {errt.response.text}")
    except requests.exceptions.RequestException as err:
        raise Exception(f"Other Error: {err}, API response: {err.response.text}")
    else:
        data = response.json()

        return data


def main():
    parser = argparse.ArgumentParser(
        description='Batch update organization members\' user attributes using members\' email addresses as identifiers')
    parser.add_argument(
        '--env', type=str, required=True, help='env to use: [production | staging].')
    parser.add_argument(
        '--cloud', type=str, required=True, help='Cloud to use: [aws | gcp]')
    parser.add_argument(
        '--client_id', type=str, required=True, help='Client ID generated from within Sigma')
    parser.add_argument(
        '--client_secret', type=str, required=True, help='Client secret API token generated from within Sigma')
    parser.add_argument(
        '--csv', type=str, required=True, help='CSV file containing members\' email addresses and their user attributes to be updated. Column names are case sensitive. Required column: Email, Optional columns: First Name,Last Name,New Email,Member Type, isArchived')
    parser.add_argument(
        '--abort_on_update_fail', type=str, required=False, help='should script abort and not try to update the next member when an attempted update fails for the current member? [enable]'
    )

    args = parser.parse_args()
    client = SigmaClient(args.env, args.cloud, args.client_id, args.client_secret)


    # Get all members for the organization and make a dict of their emails and memberIds
    try:
        members = get_all_members(client)
    except Exception as e:
        print(f"{e}")
        raise SystemExit("Script aborted")
    members_dict = {}
    for m in members:
     members_dict[m['email']] = m['memberId']

    updated_members = []
    with open(args.csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            updated_members.append(row)

    for m in updated_members:
        try:
            if len(m['Email']) > 1:
                member_email = m['Email']
            else:
                member_email = None
        except KeyError:
            print(f"\u2717 CSV FILE ERROR!")
            print(f"A column titled \"Email\" is a required column in the CSV for this script to be able to run")
            print(f"###")
            raise SystemExit("Script aborted")

        # This block of try/excepts sets the variables that get used as the request payload's values for the optional columns 
        # They will be set to None if the column itself is absent or if its value is blank/empty
        # These KeyErrors do not apply to the --abort_on_update_flag option
        try:
            if len(m['First Name']) > 1:
                member_first_name = m['First Name']
            else:
                member_first_name = None
        except KeyError:
                member_first_name = None
        try:
            if len(m['Last Name']) > 1:
                member_last_name = m['Last Name']
            else:
                member_last_name = None
        except KeyError:
                member_last_name = None
        try:
            if len(m['New Email']) > 1:
                member_new_email = m['New Email']
            else:
                member_new_email = None
        except KeyError:
                member_new_email = None
        try:
            if len(m['Member Type']) > 1:
                member_type = m['Member Type']
            else:
                member_type = None
        except KeyError:
                member_type = None
            archived_value = m.get('isArchived', None)
            if archived_value == "True":
                member_isArchived = True
            elif archived_value == "False":
                member_isArchived = False
            else:
                member_isArchived = None

        try:
            member_id = members_dict[member_email]
        except KeyError:
            print(f"\u2717 UPDATE FAILURE!")
            print(f"Member email: {member_email}")
            print(f"This email address is either invalid, or is not found, or is for a deactivated account (reactivate the account first to change its user attributes)")
            print(f"###")
            if args.abort_on_update_fail == "enable":
                raise SystemExit("Script aborted")
        else:
            payload = {}
            if member_first_name:
                    payload['firstName'] = member_first_name
            if member_last_name:
                    payload['lastName'] = member_last_name
            if member_new_email:
                    payload['email'] = member_new_email
            if member_type:
                payload['memberType'] = member_type
            if member_isArchived is not None :
                payload['isArchived'] = member_isArchived

            try:
                update_member_response = update_member(client, member_id, payload)
            except Exception as e:
                print(f"\u2717 UPDATE FAILURE!")
                print(f"Member email: {member_email}")
                print(f"The below API error prevented an update being applied for this member:")
                print(f"{e}")
                if e.args[0] == 404:
                    print(f"If the 404 error message is \"Member type name is not found\", the Member Type specified is invalid/not in use")
                if e.args[0] == 409:
                    print(f"If the 409 error message is \"Duplicate record\", the New Email specified is in use by an existing member")
                print(f"###")
                if args.abort_on_update_fail == "enable":
                    raise SystemExit("Script aborted")
            else:
                if member_first_name is None and member_last_name is None and member_new_email is None and member_type is None and member_isArchived is None:
                    print(f"\u2013 UPDATED NOTHING!")
                    print(f"Member email: {member_email}")
                    print(f"There were no user attribute values included in the CSV for this member")
                    print(f"###")
                else:
                    print(f"\u2713 UPDATE SUCCESS!")
                    print(f"Member email: {member_email}")
                    if member_first_name:
                        print(f"First Name updated to: {update_member_response['firstName']}")
                    if member_last_name:
                        print(f"Last Name updated to: {update_member_response['lastName']}")
                    if member_new_email:
                        print(f"Email updated to: {update_member_response['email']}")
                    if member_type:
                        print(f"Member type updated to: {update_member_response['memberType']}")
                    if member_isArchived is True:
                        print(f"isArchived updated to: {update_member_response['isArchived']}")
                    if member_isArchived is False:
                        print(f"isArchived updated to: {update_member_response['isArchived']}")
                    print(f"###")

if __name__ == '__main__':
    main()
