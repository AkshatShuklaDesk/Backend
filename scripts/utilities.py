from typing import Any, Optional
from fastapi import HTTPException
import requests
import base64
import os
from PIL import Image
from io import BytesIO
import pandas as pd
from random import randint

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def fetch_area_details_from_pincode(
        pincode: Optional[str]
) -> Any:
    response = requests.get(f'https://api.postalpincode.in/pincode/{pincode}')
    data = response.json()[0]

    # if data['Status'] == 'Error' or data['Status'] == '404':
    #     raise HTTPException(status_code=404, detail="pincode not valid or not record found")

    if data['Status'] == 'Success':
        details = data['PostOffice'][0]
        area = details['District']
        state = details['State']
        country = details['Country']
        result = {"Area": area, "State": state, "Country": country}
        return result
    else:
        raise HTTPException(status_code=404, detail="pincode not valid or no record found")

def decode_base64_to_image(base64_string, output_filename,output_directory):
    try:
        # Remove potential newlines and extra spaces
        base64_string = base64_string.replace('\n', '').replace('\r', '').strip()

        # Add padding if necessary to make the string length a multiple of 4
        padding = '=' * (-len(base64_string) % 4)
        base64_string += padding

        # Attempt to decode the base64 string
        image_data = base64.b64decode(base64_string, validate=True)

        # Create an image from the decoded data and save it
        image_path = os.path.join(output_directory, output_filename)
        image = Image.open(BytesIO(image_data))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.save(image_path)
        print(f"Image saved as '{output_filename}'")
    except (base64.binascii.Error, ValueError) as e:
        print(f"Error decoding base64 string: {e}")
        # Handle the error accordingly (e.g., log the error, exit the function, etc.)
    except IOError as e:
        print(f"Error in saving the image: {e}")

def read_data(is_excel, file_name):
    """
    This method will read file. It will read excel if flag is 1, or it will read csv
    :param is_excel_or_csv:
    :return: df
    """
    if is_excel:
        df = pd.read_excel(file_name.read())
    else:
        df = pd.read_csv(file_name)
    return df

def converting_data_frame_to_dict_form(df):
    """
    This method will convert data frame into dictionary form.
    :return: dict_df
    """
    df_dict = {}
    for i in range(len(df)):
        df_dict[i] = []
        df_dict[i].append(df.iloc[i].to_dict())
    return df_dict

def get_data_from_file(file):
    is_excel = False
    if file.filename.endswith('.xlsx'):
        is_excel = True
    data_df = read_data(is_excel=is_excel, file_name=file.file)
    data_df_dict = converting_data_frame_to_dict_form(df=data_df)
    return data_df_dict