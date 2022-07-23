# Sigma Sample API

This repository contains example scripts that use Sigma's public API. This is intended as a quickstart for interacting with the API and understanding common patterns and flows.

See [the Developer Documentation](https://help.sigmacomputing.com/hc/en-us/sections/4408551771411-API-Get-Started) for more details on how to get started.

## batch_update_users.py instructions  

Clone or download this repo for the script and its required Pipfile. The specific script is named `batch_update_users.py`

> Note: you will need to have API credentials for a Sigma user account with Administrator privileges (Client Secret/Token and Client ID). See [our documentation here](https://help.sigmacomputing.com/hc/en-us/articles/4408555307027-Get-an-API-Token-and-Client-ID) for how to acquire those.

### Instructions for preparing the CSV file:

Create a specifically-formatted CSV file for our script to be able to parse the users' email addresses.

1.  Name the first column "Email" and list in the rows beneath it the current email addresses for the users whose addresses you want to change.
2.  Name the second column "New Email" and list the corresponding new email addresses for each user.    
3.  Ensure there is no trailing whitespace at the end of any of the addresses and no other columns or unnecessary data in the file. 
> See an example of this required format in the CSV file in this repo named: `example_csv_for_batch_update_users.csv`

### Instructions for preparing the runtime environment and executing the script:

1.  Install pipenv in your local system. (Install instructions are [here](http://pipenv.pypa.io/))    
2.  Navigate into the folder where the `batch_update_users.py` script is, and open up a command line terminal from there.
3. Run: `pipenv install`
> Note: the Pipfile in this Github repo must be present in the same folder when doing this as it contains the dependencies pipenv needs to be able to install the runtime environment.
4.  Replace the <> fields in the below template command with the relevant values for their corresponding options and run it:

`pipenv run python batch_update_users.py --client_id <client_id> --client_secret <client_secret> --csv <path_to_your_csv_file> --env production --cloud <aws | gcp>`
> Note: you will select either "aws" or "gcp" for the "--cloud" option depending on which instance your Sigma is running.

Example run command:  

`pipenv run python batch_update_users.py --client_id 123 --client_secret abc --csv ./update_emails.csv --env production --cloud gcp`