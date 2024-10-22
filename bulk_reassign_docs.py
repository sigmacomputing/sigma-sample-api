#!/usr/bin/env python3

import argparse
import requests
from utils import SigmaClient


def get_member_id(client, user_email):
    """ Update member

        :access_token:  Generated access token
        :user_email:    Users email

        :returns:       ID associated with the user_email
    """
    try:
        response = client.get(
            f"v2/members?search={user_email}"
        )
        response.raise_for_status()
    # HTTP and other errors are handled generally by raising them as exceptions to be surfaced in downstream code
    except requests.exceptions.HTTPError as errh:
        # The API response's message value is sent in lieu of the full response to display to the user for clarity
        raise Exception(errh.response.status_code,
                        f"API message: {errh.response.json()['message']}")
    except requests.exceptions.ConnectionError as errc:
        raise Exception(
            f"Connection Error: {errc}, API response: {errc.response.text}")
    except requests.exceptions.Timeout as errt:
        raise Exception(
            f"Timeout Error: {errt}, API response: {errt.response.text}")
    except requests.exceptions.RequestException as err:
        raise Exception(
            f"Other Error: {err}, API response: {err.response.text}")
    else:
        data = response.json()
        if len(data['entries']) == 0:
            print("No users found with this email:", user_email)
            raise SystemExit("Script aborted")
        elif len(data['entries']) > 1:
            print("More than one user found with the provided email:", user_email)
            raise SystemExit("Script aborted")
        else:
            return data['entries'][0]['memberId']


def get_member_files(client, user_id):
    """ Update member
        :user_id:       id of current owner

        :returns:       an array of file objects

    """
    data = []
    moreResults = True
    next_page = ''
    while moreResults:
        try:
            # currently looks for workbooks and datasets but can be changed as needed
            response = client.get(
                f"v2/members/{user_id}/files?typeFilters=workbook&typeFilters=dataset&limit=1000{next_page}"
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as errh:
            raise Exception(
                f"Connection Error: {errh}, API response: {errh.response.text}")
        except requests.exceptions.ConnectionError as errc:
            raise Exception(
                f"Connection Error: {errc}, API response: {errc.response.text}")
        except requests.exceptions.Timeout as errt:
            raise Exception(
                f"Timeout Error: {errt}, API response: {errt.response.text}")
        except requests.exceptions.RequestException as err:
            raise Exception(
                f"Other Error: {err}, API response: {err.response.text}")
        else:
            resp = response.json()
            data = data + resp['entries']
            if resp['nextPage'] is None:
                moreResults = False
            else:
                page_id = str(resp['nextPage'])
                next_page = f'&page={page_id}'
    return data


def update_file(client, user_id, file_id, folder_id):
    """ Update file

        :access_token:  Generated access token
        :user_id:        ID of the new owner
        :file_id:       File to transfer ownership of

        :returns:       Response JSON

    """
    updateFileBody={"ownerId": user_id}
    if folder_id:
        # we need to make sure this person owns the folder
        try:
            response = client.get(
            f"v2/files/{folder_id}",
            )
            response.raise_for_status()
        # HTTP and other errors are handled generally by raising them as exceptions to be surfaced in downstream code
        except requests.exceptions.HTTPError as errh:
            raise Exception(errh.response.status_code,
                            f"API message: {errh.response.json()['message']}")
        except requests.exceptions.ConnectionError as errc:
            raise Exception(
                f"Connection Error: {errc}, API response: {errc.response.text}")
        except requests.exceptions.Timeout as errt:
            raise Exception(
                f"Timeout Error: {errt}, API response: {errt.response.text}")
        except requests.exceptions.RequestException as err:
            raise Exception(
                f"Other Error: {err}, API response: {err.response.text}")
        else:
            get_folder_response = response.json()
            if get_folder_response['type'] == "folder":
                updateFileBody["parentId"] = folder_id
            else:
                print("Provided folder_id not found")
                raise SystemExit("Script aborted")
    try:
        response = client.patch(
            f"v2/files/{file_id}",
            json=updateFileBody
        )
        response.raise_for_status()
    # HTTP and other errors are handled generally by raising them as exceptions to be surfaced in downstream code
    except requests.exceptions.HTTPError as errh:
        # The API response's message value is sent in lieu of the full response to display to the user for clarity
        # Certain error response messages are useful for the user troubleshoot common issues, such as invalid Member Type or New Email already in use
        raise Exception(errh.response.status_code,
                        f"API message: {errh.response.json()['message']}")
    except requests.exceptions.ConnectionError as errc:
        raise Exception(
            f"Connection Error: {errc}, API response: {errc.response.text}")
    except requests.exceptions.Timeout as errt:
        raise Exception(
            f"Timeout Error: {errt}, API response: {errt.response.text}")
    except requests.exceptions.RequestException as err:
        raise Exception(
            f"Other Error: {err}, API response: {err.response.text}")
    else:
        data = response.json()
        print("transfer of document:", file_id, "---", response)
        return data


def main():
    parser = argparse.ArgumentParser(
        description='Transfer all a users documents to another user')
    parser.add_argument(
        '--env', type=str, required=True, help='env to use: [production | staging].')
    parser.add_argument(
        '--cloud', type=str, required=True, help='Cloud to use: [aws | gcp | azure]')
    parser.add_argument(
        '--client_id', type=str, required=True, help='Client ID generated from within Sigma')
    parser.add_argument(
        '--client_secret', type=str, required=True, help='Client secret API token generated from within Sigma')
    parser.add_argument(
        '--curr_owner', type=str, required=True, help='Email of Org Member who currently owns the documents')
    parser.add_argument(
        '--new_owner', type=str, required=True, help='Email of Org Member who you want to transfer the documents to')
    parser.add_argument(
        '--new_folder', type=str, required=False, help='Optional folder to place the files in')

    args = parser.parse_args()
    client = SigmaClient(args.env, args.cloud,
                         args.client_id, args.client_secret)

    # we need to confirm that both the existing user and new user are valid "check_users" fn
    try:
        curr_owner_id = get_member_id(client, args.curr_owner)
    except Exception as e:
        print(f"{e}")
        raise SystemExit("Script aborted")

    try:
        new_owner_id = get_member_id(client, args.new_owner)
    except Exception as e:
        print(f"{e}")
        raise SystemExit("Script aborted")

    # get files of curr_user
    try:
        member_files = get_member_files(client, curr_owner_id)
    except Exception as e:
        print(f"{e}")
        raise SystemExit("Script aborted")

    # filter to only docs they own
    filtered_arr = [file for file in member_files if file['ownerId'] == curr_owner_id]
    # loop through and reassign ownership
    for owned_doc in filtered_arr:
        try:
            update_file(client, new_owner_id, owned_doc['id'], args.new_folder)
        except Exception as e:
            print(f"{e}")
            raise SystemExit("Script aborted")


if __name__ == '__main__':
    main()