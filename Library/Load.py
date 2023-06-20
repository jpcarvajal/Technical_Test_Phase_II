import requests
import json

import pandas as pd

def load_df_from_csv(filename: str) -> pd.DataFrame:
    """
    Description:
        Load a DataFrame from a CSV file.

    Arguments:
        - filename: The path to the CSV file.

    Returns:
        - df: The loaded DataFrame.

    Notes:
        - This is intended for the csv with processed data so no processing is required
    """
    df = pd.read_csv(filename)
    return df

def create_contact(firstname: str, lastname: str, email: str, country: str, city: str, phone: str, original_create_date: str, original_industry: str, temporary_id: str,
                    access_token_key: str) -> None:
    """
    Description:
        Set a contact in HubSpot CRM using the provided information.

    Arguments:
        - firstname: The first name of the contact.
        - lastname: The last name of the contact.
        - email: The email address of the contact.
        - country: The country of the contact.
        - city: The city of the contact.
        - phone: phone including the country code.
        - original_create_date: technical_test___create_date.
        - original_industry: string of a single industry or multiple industries concatenated with a ; including one before the first industry, eg ";Milk;Fish...".
        - temporary_id: hs_object_id.
        - access_token_key: The access token key for authentication.

    Returns:
        - None

    Notes:
        - This function sends a POST request to the HubSpot API to create a contact with the provided information.
        - If there's a single industry in the original_industry parameter, no semicolons are present.
        - The values for original industry must be among "Fruit and vegetables", "Bakery products", "Poultry and fish", "Dairy products", "Milling", "Meat", "Animal feeds".
        - NaN values or "" aren't allowed and result in an error.
    """

    url = 'https://api.hubapi.com/crm/v3/objects/contacts'
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token_key}"}
    payload = {
                "properties": {
                "firstname" : firstname,
                "lastname" : lastname,
                "email" : email,
                "country" : country,
                "city" : city,
                "phone" : phone,
                "original_create_date" : original_create_date,
                "original_industry" : original_industry,
                "temporary_id" : temporary_id
                }
            }
    
    requests.post(url, headers=headers, data=json.dumps(payload))

def load_into_hubspot(access_token_key: str, filename: str) -> None:  
    """
    Load data of contacts from a CSV file into HubSpot CRM.

    Arguments:
        - access_token_key: The access token key for authentication.
        - filename: The path to the CSV file.

    Returns:
        - None
    """
    df = load_df_from_csv(filename)
    df.apply(lambda x: create_contact(x['firstname'], x['lastname'], x['email'], x['country'], x['city'], x['phone'], x['technical_test___create_date'], x['industry'],
                                      str(x['hs_object_id']), access_token_key), axis=1)