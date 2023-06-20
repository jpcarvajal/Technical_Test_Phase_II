import pandas as pd
import re
from typing import List, Dict, Tuple

#from geopy.geocoders import Nominatim
#import phonenumbers
#import country_converter as coco

def load_df_from_csv(filename: str) -> pd.DataFrame:
    """
    Description: Loads a csv file as a pandas dataframe, transforms the name of it's columns, eliminating "properties." from them and returns the dataframe.

    Arguments:
        - filename: Name or path of the csv.

    Returns:
        - df: Dataframe made from the csv data and with some of it's column names modified.
    """
    df=pd.read_csv(filename)
    df.columns = df.columns.str.replace('properties.','')
    return df

"""My initial solution for this problem used the geolocation library and can be seen at the end of this file, it's more robust, using the library to get any country but a lot slower
due to the api calls used, it could be efficient by writing on a file the results as they're searched and only using the api for the ones that haven't been searched yet but I feel like 
this would go against the intentions of the test so I didn't implement it."""
def load_country_city_database() -> Dict[str, List]:
    """
    Description: Returns a database of countries and it's cities.

    Returns:
        - Tuple[str, str]: Tuple containing the recognized country and the city.

    Notes:
        - A bigger and more robust could be built using the libraries I mentioned before.
    """  
    locations = {'England': ['Plymouth','Milton Keynes','Oxford','London','Winchester'], 'Ireland': ['Waterford','Limerick','Dublin','Cork']}
    return locations

def country_recognition(place: str) -> Tuple[str, str]:
    """
   Description: Recognize the country associated with a given place using a database of known country city relationships.

    Arguments:
        - place : The name of the place to be recognized, either a city or a country.

    Returns:
        - Tuple[str, str]: Tuple containing the recognized country and the city.

    Notes:
        - If the place is NaN (null), it returns ("Nan", "Nan"), this is so because i can't upload null data into hubspot.
        - If the place is a country present in the country-city database, it returns (place, "Unknown").
        - If the place is recognized as a city in the country-city database, it returns the corresponding country and the place itself.
        - If the place is not recognized, it returns ("Unknown", "Not recognized") because It's more likely for a city to not be recognized.
    """       
    locations = load_country_city_database()

    if pd.isnull(place):
        return ("Nan", "Nan")
    elif place in locations.keys():
        return (place, "Unknown")
    else:
        city_found = False 
        for country, cities in locations.items():
            for city in cities:
                if place.lower() == city.lower():
                    city_found = True
                    country_found = country
                    
    if city_found:
        return (country_found, place)
    else:
        return ("Unknown","Not recognized")
    
def split_column_of_tuples(df: pd.DataFrame, old_column: str, new_column_1: str, new_column_2: str) -> pd.DataFrame:
    """
    Description: Split a column containing tuples into two separate columns. 

    Arguments:
        - df: The DataFrame containing the data.
        - old_column: The name of the column to be split.
        - new_column_1: The name of the first new column.
        - new_column_2: The name of the second new column.

    Returns:
        - df: The updated DataFrame with the new columns.

    Notes:
        - It's main use is to split the city_country column and it's done mainly for the management of null values.
        - If a tuple is missing a value, the corresponding new column will contain an empty string ('').
    """
    df[[new_column_1, new_column_2]] = df[old_column].apply(lambda x: pd.Series(x))
    df[new_column_2].fillna('', inplace=True) 
    return df

def found_emails(raw_email: str, pattern: str = '<(.*)>') -> str:      
    """
    Description: Extracts an email address from a raw email string using a pattern.

    Arguments:
        - raw_email: The raw email string from which to extract the email address. It follows the pattern "any characters <(email)> any characters".
        - pattern: The regular expression pattern used to match and extract the email address. 
                   Default is '<(.*)>'.

    Returns:
        - The extracted email address as a string.

    Notes:
        - If the raw_email is empty or null, an empty string is returned.
        - If the pattern does not match the raw_email, the function prints a message 
          and returns the input raw_email, this is so the user knows that the pattern needs to be changed.
        - The default is the one that correctly identifies emails but the parameter is added
          so the function can be used on other patterns.
    """
    if pd.isnull(raw_email):
        return ""
    else:
        try:
            email = re.search(pattern, raw_email)
            return email.group(1)
        except AttributeError:
            print ('Incorrect pattern, returning input')
            return raw_email
        
"""
In a similar fashion to the country recognition function, my first solution used the library phonenumbers and country_converter but it was slow,
I also added it at the end of the file and the use of a file, as explained in the country recognition function would make it efficient by saving the results as they're found.
"""
def country_codes_database(country: str) -> str:
    """
    Description: Returns a database of countries and it's phone codes.

    Returns:
        - Tuple[str, str]: Tuple containing the recognized country and the city.

    Notes:
        - A bigger and more robust could be built using the libraries I mentioned before.
        - If the country isn't found, an empty string is returned
    """  
    codes = {'Great Britain': '+44', 'Ireland': '+353'}
    if country in codes.keys():
        return codes[country]
    else:
        return ""

def fix_phone_numbers(raw_phone: str, country: str) -> str: 
    """
    Description: Formats a raw phone number based on the specified country.

    Arguments:
        - raw_phone: The raw phone number string to be formatted.
        - country: The country associated with the phone number.

    Returns:
        - The formatted phone number as a string.

    Notes:
        - If the raw_phone is empty or null, "Nan" is returned.
        - If the country is one of 'England', 'Wales', 'Northern Ireland', 'Scotland',
          it is considered as 'Great Britain' for phone number formatting purposes, included this clause 
          because many libraries and datasets that I explored only contain Great Britain as a country.
        - The raw_phone is stripped of non-digit characters and leading zeros.
        - The formatted phone number is returned in the format "(country_phone_code) xxxx xxx...".
    """
    if  pd.isnull(raw_phone):
        return "Nan"
    else:
        country = country
        if country in ['England', 'Wales', 'Northern Ireland', 'Scotland']:
            country = 'Great Britain'
 
        phone_code = country_codes_database(country)
        
        raw_phone = re.sub('\D', '', raw_phone)
        phone_numbers = raw_phone.lstrip('0')
        phone = f"({phone_code}) " + phone_numbers[:4] + " " + phone_numbers[4:] 
        return phone

def name_from_email(email: str, pattern: str = '([a-z]+)_([a-z]+)') -> str: 
    """
    Description: Extracts the full name from an email using a pattern.

    Arguments:
        - email: The email string from which to extract the name. It follows the pattern "any characters <firstname_lastnameNumbers@emailDomain> any characters"
        - pattern: The regex pattern to match and extract the name. Defaults to '([a-z]+)_([a-z]+)'.

    Returns:
        - The extracted full name as a string capitalized.

    Notes:
        - The function assumes that the name can be identified from the email using the specified pattern, if it isn't this functions shouldn't be used.
        - The pattern should contain two capturing groups to extract the first and last name.
    """
    name = re.search(pattern, email)
    return name.group(1).capitalize() + " " + name.group(2).capitalize()

def generate_name(row: pd.Series) -> str:
    """
    Description:
        Generate a name from the first name and last name, or email.

    Arguments:
        - row: A pandas Series containing the relevant columns (firstname, lastname, raw_email).

    Returns:
        - str: The generated name as a string.

    Notes:
        - This is done because according to the duplicates management explanation the full name would work as an unique identifier that can be linked to an email on
         different records, and since the name can be inferred from the email, the rows that don't have a name but have an email, can still be treated as having a unique
         identifier and in that way relate them to their owner, since there can only be one person with that email.
        -Again, this function assumes that the name can be identified from the email using the specified pattern, if it isn't, this functions shouldn't be used.
        - If both the first name and last name are missing or empty, the name is generated from the email.
        - If the raw email is missing or empty, an empty string is returned.
        - The generated name is returned as a combination of the first name and last name, separated by a space.
    """
    if (pd.isnull(row['firstname']) and pd.isnull(row['lastname'])) or (row['firstname'] == "" and row['lastname'] == ""):
        if row['raw_email'] == "" or pd.isnull(row['raw_email']):
            return ""
        else:
            return name_from_email(row['raw_email'])
    else:
        return row['firstname'] + " " + row['lastname']

def concat_industries(df: pd.DataFrame, values: List) -> List[int]:
    """
    Description:
        Concatenate all of the industries that a person has had with a semicolon and updating the value of the most recent record of each contact, 
        finally returns the index of these recent records.

    Arguments:
        - df: The DataFrame containing the data.
        - values: A list of tuples representing the latest record's index and the industry values that that contact has had over time.

    Returns:
        - List[int]: A list of indexes corresponding to the records that were updated.

    Notes:
        - The function updates the 'industry' column of the DataFrame by concatenating multiple industries with a semicolon, including one before the first industry, eg
         ;Meat;Milling.
        - Although a different function that returns the indexes would make more sense from a modular approach, 
         since this function is already going through the list where the indexes are saved, it's more efficient in this way.
    """
    indexes = []
    for value in values:
        index = value[0]
        indexes.append(index)
        industries = value[1]
        if len(industries) > 1:
            industries = ";" + ";".join(industries)
            df.at[index, 'industry'] = industries
    
    return indexes

def duplicate_management(df: pd.DataFrame) -> pd.DataFrame: 
    """
    Description:
        Perform duplicate management on a DataFrame based on email and full name matching, keeping only the latest records and updating their missing values 
        with values from order records except on the industry value, where all of the previous values are concatenated using ; for future uploading into hubspot.

    Arguments:
        - df: The DataFrame containing the data.

    Returns:
        - pd.DataFrame: The updated DataFrame with only the most recent records per contact and with the industry values concatenated.

    Notes:
        - The criteria to define which one was the latest record was the 'createdAt' column, I chose this one only because of the example given, maybe another one like updatedAt 
         would be a better choice.
        - The function iterates over the DataFrame and keeps track of the latest occurrence of each name (generating a name from the email if the name isn't present in the record).
        - If a record with the same name is encountered again, the function updates missing values in the latest occurrence with values from the current record except for "industry".
        - The 'industry' column is concatenated with a semicolon for multiple occurrences of the same name, with the latest record's industry listed first.
        - The dictionary has a structure of  {email: [index,[industries]]}
        - The function returns the DataFrame with only the latest records.
    """
    df['createdAt'] = pd.to_datetime(df['createdAt']) 
    df.sort_values(by=['createdAt'], ascending=False, inplace = True)
    
    first_records = {} 

    for index, row in df.iterrows(): 

        name = generate_name(row)
        if name == "":
            continue

        if name not in first_records.keys():
            first_records[name] = [index, [row['industry']]]            
        else:
            index_of_latest = first_records[name][0]
            for column in df.columns:
                if column == 'industry':
                    continue 
                if (pd.isnull(df.at[index_of_latest, column]) or df.at[index_of_latest, column] == "") and (pd.notnull(row[column]) and row[column] != "") :
                        #Updates if the latest record has a missing value that an older one has
                        df.loc[index_of_latest, column] = row[column] 

            if row['industry'] not in first_records[name][1]:
                first_records[name][1].insert(0, row['industry']) #Inserted at the start of the list according to the example

    # Obtain indexes of the latest records and concatenate industries
    indexes = concat_industries(df, first_records.values())
    
    # Filter the DataFrame based on the indexes of the latest records
    df=df.loc[indexes, :]

    return df


#----------------------------------------------------------------------------------------------------------------------------------------------
""" def country_recognition(place: str) -> Tuple[str, str]:      
        city, country = "", ""

        geolocator = Nominatim(user_agent="_")
        address = str(geolocator.geocode(place)).split(', ') #Address looks like ['Winchester', 'Hampshire', 'England', 'United Kingdom']

        if address is not None:
            country = address[-1]     
            if country == 'United Kingdom': #If the place is a country from the UK, the "subcountry" is at the second to last place in the address
                country = address[-2]
                if len(address) > 2: #If the input is a city or county
                        city = place
            elif len(address) > 1: #If the input is a city or a county in a place outside of the UK
                city = place
        else:   #If the country of the city wasn't found
            city = place

        country = country.split(" / ")[-1] #If the country has a different name on it's own language it's saved like Éire / Ireland

        return (country, city) """

#----------------------------------------------------------------------------------------------------------------------------------------------

""" def country_code(country: str) -> str:
    code =  coco.convert(names=country, to='ISO2')
    phone_code = str(phonenumbers.country_code_for_region(code))
    return phone_code

def fix_phone_numbers(raw_phone: str, country: str) -> str:
    if  pd.isnull(raw_phone):
        return ""
    else:
        country = country.upper()
        if country in ['England'.upper(), 'Wales'.upper(), 'Northen Ireland'.upper(), 'Scotland'.upper()]:
            country = 'Great Britain'
        
        phone_code = country_code(country)

        raw_phone = re.sub('\D', '', raw_phone)
        phone_numbers = raw_phone.lstrip('0')
        phone = f"(+{phone_code}) " + phone_numbers[:4] + " " + phone_numbers[4:] 
        return phone """