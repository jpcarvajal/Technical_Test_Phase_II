import requests
import json
import pandas as pd
from typing import List, Dict

def parameters_for_search(access_token_key: str, after:int = 0, ):
    """
    Description: 
        Set the parameters for each api call, updating the value after so all of the results can be saved and the access token is set.

    Arguments:
        - access_token_key: Access token, needed for authentication.
        - after: Indicates to the requests how many items should be skipped before showing the results, this is useful because the api currently returns at most 100 results at a time,
        so, in order to get the rest of the results another call has to be made skipping the already known results. It's set as 0 by default so that if it's called without this parameter
        the function returns the first 100 results and other data from the call itself.

    Returns:
        - url: String containing the url for the api call.
        - headers: Dictionary containing the Content-Type and Authorization parameters for the call, with the access token key embeded accordingly.
        - payload: Dictionary with lists in a json like format, this include the filters of the call, properties, limit and after parameter, all formatted as needed for the search api.
        
    Notes:
        - I extract the names even when tho the exercise doesn't ask me to because they're relevant for the dupe management
        -  The url could be changed according to the objects needed, same with the filters and properties and could even be changed to be parameters but I felt it would affect the readability. 
    """
    url = 'https://api.hubapi.com/crm/v3/objects/contacts/search'
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token_key}"}
    payload = {
        "filters": [
            {
                "propertyName": "allowed_to_collect",
                "operator": "EQ",
                "value": "true"
            }
        ],
        "properties": [
            "raw_email",
            "country",
            "phone",
            "technical_test___create_date",
            "industry",
            "address",
            "hs_object_id",
            "firstname",
            "lastname"
        ],
        "limit": 100,
        "after": f"{after}"
    }
    return url, headers, payload

def contact_collection(access_token_key: str, filename: str) -> str: 
    """
    Description: Make a post request on the search api for contacts, using the default values of parameters_for_search which gives the total number of results that meet the filters, using
    this value, calls are made, changing the "after" parameter until all results are fetched and saved on the variable contacts which has a List[Dict[str:str]] structure, finally the 
    function create_df_and_save_to_csv is called to save a csv with the data and return the name or path of said file. 

    Arguments:
        - access_token_key: Access token, needed for authentication.
        - filename: Name or path of the csv that will contain the extracted data.

    Returns:
        - contacts_csv: String containing the name or path of the csv on which the data was saved.
    
    Notes:
        - The max_per_page variable could be changed if the maximum number of supported objects per page is increased by the api itself
    """
    max_per_page = 100 
    url, headers, payload =  parameters_for_search(access_token_key)

    res = requests.post(url, headers=headers, data=json.dumps(payload)) 

    data = res.json()

    total = data['total']
    
    contacts = data['results']

    page = 1

    while page * max_per_page < total:
        url, headers, payload = parameters_for_search(access_token_key, after = page * max_per_page)
        res = requests.post(url, headers = headers, data = json.dumps(payload))
        contacts.extend(res.json()['results'])
        page+=1

    contacts_csv = create_df_and_save_to_csv(contacts, filename)

    return contacts_csv 

def create_df_and_save_to_csv(contacts: List[Dict[str,str]], filename: str) -> str:
    """
    Description: Takes data in a json like structure, converts it into a pandas dataframe and saves it as a csv file, returning the name or path of said file.

    Arguments:
        - contacts: Json like structure, consisting in python of a list of dictionaries of str to str values.
        - filename: Name or path of the csv.

    Returns:
        - filename: String containing the name or path of the csv on which the data was saved.
    """
    contacts_df = pd.json_normalize(contacts)    
    contacts_df.to_csv(filename, index = False)
    return filename
