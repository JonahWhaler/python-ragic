# Python Ragic
A Python client for interacting with the [Ragic API](https://www.ragic.com/intl/en/doc-api/). 
This library simplifies making requests to Ragic databases, handling authentication, and working with records.

[![PyPI Downloads](https://static.pepy.tech/badge/python-ragic)](https://pepy.tech/projects/python-ragic)

<br />

# Table of Contents
- [Python Ragic](#python-ragic)
- [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
- [Code Snippets](#code-snippets)
  - [Load Data (Table-level)](#load-data-table-level)
  - [Write new data to Ragic database](#write-new-data-to-ragic-database)
  - [Modify Data (single record)](#modify-data-single-record)
  - [Delete Data (single record)](#delete-data-single-record)
  - [Get Data (single record)](#get-data-single-record)
  - [Upload files](#upload-files)
  - [Download files](#download-files)

<br />

## Features

- Easy authentication and connection setup
- Read data
- Write new data
- Modify existing records
- Delete records
- Get single records
- Upload files
- Download files

<br />

## Getting Started
1. Get your API key from Ragic. [link](https://www.ragic.com/intl/en/doc-api/24/HTTP-Basic-authentication-with-Ragic-API-Key)

    1.1. Add environment variables to `.env` file:
    - `RAGIC_URL`
    - `RAGIC_NAMESPACE`
    - `RAGIC_API_KEY`

2. Setup `structure.yaml`.

    2.1. Follow the [structure file](docs/set-up-structure-file.md) to define the structure of your database.

    2.2. Retrieve the field id from Ragic. [link](https://www.ragic.com/intl/en/doc-api/18/Finding-the-field-id-for-a-field)
    
3. Install the package using pip:
    ```bash
    pip install python-ragic
    ```

# Code Snippets
## Load Data (Table-level)
```python
from ragic import RagicAPIClient

client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)

TAB_NAME = "Sales Management System"
TABLE_NAME = "customer"

data_dict = client.load(
    TAB_NAME,
    TABLE_NAME,
    conditions=[("gender", OperandType.EQUALS, "Male")],
    offset=0,
    size=10,
    other_get_params=OtherGETParameters(subtables=False, listing=False),
    ordering=Ordering(order_by="customer_id", order=OrderingType.ASC),
)

if data_dict:
    with open("data.json", "w", encoding="utf-8") as f:
        f.write(json.dump(data_dict, f, indent=4))
else:
    print("No data found.")
```

<br />


## Write new data to Ragic database

```python
from ragic import RagicAPIClient

client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)

TAB_NAME = "Sales Management System"
TABLE_NAME = "customer"

# For field that takes attachment, provide the file path
# If more than one file, provide a list of file paths
data_dict = {
    "Name": "John Doe",
    "Age Group": "41 - 50",
    "Race": "Chinese,
}

resp_dict = client.write_new_data(
    TAB_NAME, TABLE_NAME, data=data_dict
)
if resp_dict:
    with open("write_response.json", "w", encoding="utf-8") as f:
        f.write(json.dump(resp_dict, f, indent=4))
    print("Record created successfully.")
else:
    print("Failed to create record.")
```

<br />

## Modify Data (single record)
```python
from ragic import RagicAPIClient

client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)

TAB_NAME = "Sales Management System"
TABLE_NAME = "customer"

# For field that takes attachment, provide the file path
# If more than one file, provide a list of file paths
# When modifying a record with an attachment, 
# it adds a new file instead of replacing the existing one.

# To replace the existing file, set None to the field name, 
# Take note, this approach deletes all existing files from the field.
# Call upload_file method to upload the new file.
data_dict = {
    "Name": "John Doe",
    "Age Group": "41 - 50",
    "Race": "Chinese"
}
record_id = "<ragicId>"  # Replace with the actual record ID

resp_dict = client.modify_data(
    TAB_NAME,
    TABLE_NAME,
    data=data_dict,
    record_id=record_id
)
```

<br />

## Delete Data (single record)
```python
from ragic import RagicAPIClient
client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)

TAB_NAME = "Sales Management System"
TABLE_NAME = "customer"

record_id = "<ragicId>"  # Replace with the actual record ID

resp_dict = client.delete_data(
    TAB_NAME,
    TABLE_NAME,
    record_id=record_id
)
```

## Get Data (single record)
```python
from ragic import RagicAPIClient
client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)

TAB_NAME = "Sales Management System"
TABLE_NAME = "customer"

record_id = "<ragicId>"  # Replace with the actual record ID

resp_dict = client.get_data(
    TAB_NAME,
    TABLE_NAME,
    record_id=record_id
)
```

## Upload files
```python
from ragic import RagicAPIClient
client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)
TAB_NAME = "Sales Management System"
TABLE_NAME = "customer"
record_id = "<ragicId>"  # Replace with the actual record ID

field_name = "file_upload_field"  # Replace with the actual field name
file_path = "path/to/your/file.png"  # Replace with the actual file path

resp_dict = client.upload_file(
    TAB_NAME,
    TABLE_NAME,
    record_id=record_id,
    field_name=field_name,
    file_path=file_path
)
```

## Download files
```python
from ragic import RagicAPIClient

client = RagicAPIClient(
    base_url=None,
    namespace=None,
    api_key=None,
    version=3,
    structure_path="structure.yaml",
)

# format xxxxx@filename.file_extension
file_identifier = "<fileIdentifier>"  # Replace with the actual file identifier
output_path = "path/to/save/file.png"  # Replace with the desired output path

resp_dict = client.download_file(
    file_identifier=file_identifier,
    output_path=output_path
)
```