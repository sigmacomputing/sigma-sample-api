#!/usr/bin/env python3

import argparse
import json
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


def get_workbook_schema(access_token, workbook_id):
    """ Gets the workbook's schema

        :access_token:  Generated access token
        :workbook_id:   ID of workbook

        :returns:       Dictionary of workbook's schema

    """
    response = requests.get(
        f"{BASE_URL}/v2/workbooks/{workbook_id}/schema",
        headers=get_headers(access_token)
    )
    return response.json()


def export_workbook(access_token, workbook_id, element_id=None):
    """ Exports workbook to file

        :access_token:  Generated access token
        :workbook_id:   ID of workbook
        :element_id:    Optional element ID

        :returns:       JSON of workbook data

    """
    payload = {
        "format": {
            "type": "json"
        }
    }
    if element_id:
        payload["elementId"] = element_id

    response = requests.post(
        f"{BASE_URL}/v2/workbooks/{workbook_id}/export",
        headers=get_headers(access_token),
        json=payload
    )
    return response.json()


def write_to_file(filename, data, element_id=None):
    """ Writes export result to file

        :filename:      Filename to write to
        :data:          JSON data to write
        :element_id:    Optional element ID if multiple exports

    """
    if element_id:
        filename = f"{filename}_{element_id}"

    with open(f"{filename}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    parser = argparse.ArgumentParser(
        description='Export a workbook from Sigma into JSON')

    parser.add_argument(
        '--client_id', type=str, required=True, help='Client ID generated from Sigma')
    parser.add_argument(
        '--client_secret', type=str, required=True, help='Client secret generated from Sigma')
    parser.add_argument(
        '--workbook_id', type=str, required=True, help='ID of workbook to be exported')
    parser.add_argument(
        '--element_id', type=str, help='Optional workbook element')
    parser.add_argument(
        '--filename', type=str, help='Optional filename prefix')

    args = parser.parse_args()

    access_token = get_access_token(args.client_id, args.client_secret)
    if args.element_id:
        data = export_workbook(access_token, args.workbook_id, args.element_id)
        filename = args.filename if args.filename else args.workbook_id
        write_to_file(filename, data)
    else:
        schema = get_workbook_schema(access_token, args.workbook_id)
        elements = schema["elements"]
        print(elements)
        for element_id, _ in elements.items():
            data = export_workbook(access_token, args.workbook_id, element_id)
            filename = args.filename if args.filename else args.workbook_id
            write_to_file(filename, data, element_id)


if __name__ == '__main__':
    main()
