#!/usr/bin/env python3
import argparse
import csv
from utils import SigmaClient

'''
./manage_team.py --env production --cloud aws --client_id xxxx --client_secret xxx \
--team_id xxx --file xxx.csv
'''
def main():
    parser = argparse.ArgumentParser(
        description='Add or remove members of a team')
    parser.add_argument(
        '--env', type=str, required=True, help='env to use: [production | staging].')
    parser.add_argument(
        '--cloud', type=str, required=True, help='Cloud to use: [aws | gcp]')
    parser.add_argument(
        '--client_id', type=str, required=True, help='Client ID generated from Sigma')
    parser.add_argument(
        '--client_secret', type=str, required=True, help='Client secret generated from Sigma')
    parser.add_argument(
        '--team_id', type=str, required=True, help='ID of the team')
    parser.add_argument(
        '-a', '--add', nargs='+', type=str, help='Optional workbook element')
    parser.add_argument(
        '-r', '--remove', nargs='+', type=str, help='Optional filename prefix')
    parser.add_argument(
        '-f', '--file', type=str, help='Optional csv file with columns "member_id, operation" where operation in (add|remove)'
    )
    parser.add_argument(
        '--dry_run', action='store_true', help='Just print')

    args = parser.parse_args()
    if args.dry_run:
        print(args)
    client = SigmaClient(args.env, args.cloud, args.client_id, args.client_secret)
    payload = {
        'add': [],
        'remove': []
    }
    if args.add or args.remove:
        payload = {
            'add': args.add,
            'remove': args.remove
        }
    elif args.file:
        with open(args.file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                if row['operation'] == 'add':
                    payload['add'].append(row['member_id'])
                elif row['operation'] == 'remove':
                    payload['remove'].append(row['member_id'])
    if args.dry_run:
        print(payload)
    else:
        res  = client.patch(f'v2/teams/{args.team_id}/members', json=payload)
        print(res)

if __name__ == '__main__':
    main()