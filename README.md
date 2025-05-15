# Python Ragic
A Python client for interacting with the [Ragic API](https://www.ragic.com/intl/en/doc-api/). 
This library simplifies making requests to Ragic databases, handling authentication, and working with records.

<br />

# Table of Contents
- [Python Ragic](#python-ragic)
- [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
  - [Future Improvements](#future-improvements)

<br />

## Features

- Easy authentication and connection setup
- Read data from Ragic databases

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
4. Code snippet to get started:

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

## Future Improvements
- Update and delete records
