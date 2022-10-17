# Sigma Sample API

This repository contains example scripts that use Sigma's public API. This is intended as a quickstart for interacting with the API and understanding common patterns and flows.

See [the Developer Documentation](https://help.sigmacomputing.com/hc/en-us/sections/4408551771411-API-Get-Started) for more details on how to get started.

## batch_update_users.py

Batch update organization members' user attributes. The members' email addresses are used as identifiers for matching to their corresponding member IDs. 

The script uses the `PATCH /v2/members/{memberId}` endpoint specified in our [API documentation here](https://help.sigmacomputing.com/hc/en-us/articles/4408555573267-Organization-Member-API#h_01FWMC0K925WE07AEYS1S65Q5M).

You will need to have API credentials for a Sigma user account with Administrator privileges (Client Secret/Token and Client ID). See [our documentation here](https://help.sigmacomputing.com/hc/en-us/articles/4408555307027-Get-an-API-Token-and-Client-ID) for how to acquire those.

### Instructions 
Clone or download this repo for the script and its required Pipfile. The specific script is named `batch_update_users.py`

#### Instructions for preparing the CSV file

Create a specifically-formatted CSV file for our script to be able to parse. The headers do not need to be ordered, but the script is case sensitive to their names.
> See an example of this required format in the CSV file in this repo named: [example_csv_for_batch_update_users.csv](examples/example_csv_for_batch_update_users.csv)

**Required header:** Email
**Optional headers:** First Name,Last Name,New Email,Member Type

The values for the "Email" column will be the email addresses of the users whose attributes you want to update.

You are free to include or exclude any of the optional columns depending on which user attributes you want to update.

For example, if you only want to update users' email addresses, your headers would be: `Email,New Email`

If you wanted to update a mixture of attributes for some users but not others, then leave the values you don't want updated blank for those users. 

Ensure there is no trailing whitespace at the end of any of the addresses and no other columns or unnecessary data in the file.

#### Instructions for preparing the runtime environment

1. Install Python3. [Instructions here](https://www.python.org/downloads/).
2.  Install pipenv. [Instructions here](http://pipenv.pypa.io/)
3.  In a command line terminal, navigate into the folder where the `batch_update_users.py` script is and run: `pipenv install` 
    > The Pipfile in this Github repo must be present in the same folder when running this command. It contains information about the dependencies pipenv needs to install inside the virtual environment for the script to use. You will see that a file called "Pipfile.lock" gets created when doing this.
    
#### Instructions for executing the script

Replace the `<>` fields in the below template command with the relevant values for their corresponding arguments:

`pipenv run python batch_update_users.py --client_id <client_id> --client_secret <client_secret> --csv <path_to_your_csv_file> --env production --cloud <aws | gcp>`

|Argument|Description|Required?
|--|--|--|
| **client_id** | Client ID generated from within Sigma |Yes
| **client_secret** | Client Secret (API token) generated from within Sigma |Yes
| **csv** | Path to CSV file |Yes
| **env** | Environment to use: production or staging. You should use production |Yes
| **cloud** | Cloud provider your Sigma instance is on: aws or gcp |Yes
| **abort_on_update_fail** | Script should abort on any update error: enable |No

> You will select either "aws" or "gcp" for the " --cloud" option depending on which provider your Sigma instance is running on. You can see which cloud yours is inside Sigma by going to Administration->Account->General Settings. (We need to know this because there are [separate APIs for each](https://help.sigmacomputing.com/hc/en-us/articles/4408835546003-Get-Started-with-Sigma-s-API#ite))

Example run command:

`pipenv run python batch_update_users.py --client_id 123 --client_secret abc --csv ./update_emails.csv --env production --cloud gcp`

> By default, when the script encounters an error attempting to update a particular member's metadata, it will print the error and move on to try update the next member listed in the CSV. 
>
>If you want to abort the script when it encounters any such error, you can include the optional argument: `--abort_on_update_fail enable`

Example run command with optional argument to abort on any update error:

`pipenv run python batch_update_users.py --client_id 123 --client_secret abc --csv ./update_emails.csv --env production --cloud gcp --abort_on_update_fail enable`
