#!/usr/bin/env python3

import argparse
import json
import time

from utils import SigmaClient


def get_workbook_schema(client, workbook_id):
    """ Gets the workbook's schema

        :access_token:  Generated access token
        :workbook_id:   ID of workbook

        :returns:       Dictionary of workbook's schema

    """
    response = client.get(
        f"v2/workbooks/{workbook_id}/schema",
    )
    return response.json()


def export_workbook(client, workbook_id, export_format='json', element_id=None, retries=5):
    """ Exports workbook to file

        :access_token:  Generated access token
        :workbook_id:   ID of workbook
        :element_id:    Optional element ID

        :returns:       JSON of workbook data

    """
    payload = {
        "format": {
            "type": export_format
        }
    }
    if element_id:
        payload["elementId"] = element_id

    response = client.post(
        f"v2/workbooks/{workbook_id}/export",
        json=payload
    )
    try:
        query_id = response.json()['queryId']
        return query_id
    except:
        err = {'status_code': response.status_code, 'content': response.text, 'retries': retries}
        print(f'error: {err}')
        if retries < 0:
            raise
        return export_workbook(client, workbook_id, export_format, element_id, retries - 1)


def retrieve_results(client, query_id):
    res = None
    while res is None:
        time.sleep(10)

        response = client.get(
            f'v2/query/{query_id}/download',
        )
        if response.status_code == 200:
            res = response.content
        elif response.status_code != 204:
            print(f'status: {response.status_code}, content: {response.text}')
    return res


def write_to_file(filename, content, export_format='json', element_id=None):
    """ Writes export result to file
        :filename:      Filename to write to
        :data:          JSON data to write
        :element_id:    Optional element ID if multiple exports
    """
    if element_id:
        filename = f"{filename}_{element_id}"

    with open(f"{filename}.{export_format}", 'wb') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(
        description='Export a workbook from Sigma into JSON')
    parser.add_argument(
        '--env', type=str, required=True, help='env to use: [production | staging].')
    parser.add_argument(
        '--cloud', type=str, required=True, help='Cloud to use: [aws | gcp]')
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
    parser.add_argument(
        '--format', type=str, default='json', help='Optional format: [csv | json | pdf]')

    args = parser.parse_args()

    client = SigmaClient(args.env, args.cloud, args.client_id, args.client_secret)
    if args.element_id:
        query_id = export_workbook(client, args.workbook_id, args.format, args.element_id)
        content = retrieve_results(client, query_id)
        filename = args.filename if args.filename else args.workbook_id
        write_to_file(filename, content, args.format)
    else:
        schema = get_workbook_schema(client, args.workbook_id)
        elements = schema["elements"]
        print(elements)
        for element_id, _ in elements.items():
            query_id = export_workbook(client, args.workbook_id, args.format, element_id)
            content = retrieve_results(client, query_id)
            filename = args.filename if args.filename else args.workbook_id
            write_to_file(filename, content, args.format, element_id)


if __name__ == '__main__':
    main()
