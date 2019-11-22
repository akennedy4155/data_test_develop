# Alex Kennedy 11-22-19
from src.xml_parse_to_csv import read_xml_to_tree, bulk_extract, stringify_bulk_extract
import pandas as pd
import datetime
import re

# get the xml tree
url = "http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml"
tree = read_xml_to_tree(url)

# bulk extract the columns that we want
row_tag = "Listing"

# Some fields use dot notation to represent ancestry of the element, used to resolve AmbiguousElement exceptions
basic_fields = [
    "MlsId",
    "MlsName",
    "DateListed",
    "Location.StreetAddress",
    "Price",
    "Bedrooms",
    "Bathrooms",
    "BasicDetails.Description"
]

list_fields = [
    {
        "list_tag": "Appliances",
        "list_element_tag": "Appliance"
    },
    {
        "list_tag": "Rooms",
        "list_element_tag": "Room"
    }
]

row_dicts = bulk_extract(
    tree.getroot(),
    row_tag,
    elements_basic=basic_fields,
    elements_list=list_fields
).values()

row_list = [stringify_bulk_extract(row) for row in row_dicts]

df = pd.DataFrame(row_list)

# date listed == 2016
df["year"] = df["DateListed"].apply(datetime.datetime.strptime, args=('%Y-%m-%d %H:%M:%S',))
df["year"] = df["year"].apply(lambda x: x.year)
df = df[df["year"] == 2016]

# filter description "and"
df["description_and"] = df["BasicDetails.Description"].apply(lambda x: bool(re.search(r".*and.*", x)))
df = df[df["description_and"]]

# order by date listed
df.sort_values(by=["DateListed"], inplace=True)

# reorder and get columns
order = basic_fields + [field["list_tag"] for field in list_fields]
df = df[order]

df.to_csv('zillow_data.csv', index=False)
