# Introduction
This file describes the structure of the YAML file (`structure.yaml`) used to mirror the database structure in Ragic database. It enable user to interact with the database in more user-friendly way, define data operations using the field name instead of the field id.

<br />

# Table of Contents
- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
    - [FieldType](#fieldtype)
    - [Field](#field)
    - [Fields](#fields)
    - [Table](#table)
    - [Tables](#tables)
    - [Tab](#tab)
- [Example](#example)
  - [Sales Management System](#sales-management-system)

<br />

### FieldType
The field type is used to define the type of data that can be stored in a field. Only a limited set of field types are supported.
The following field types are supported:
- text
  - text:date
  - text:email
  - text:phone
- rich text
- number
- selection
- multiple select

<br />

### Field
Bracket notation is used to indicate that the field name is a placeholder and should be replaced with the actual field name. The field name should be unique within the `fields`.

```yaml
<field_name>: 
    field_id: {{String}}                        # mandatory, unique field id copied from Ragic
    field_type: {{FieldType}}                   # mandatory, [text | rich text | number | selection | multiple select]
    allow_user_add_new_options: {{Boolean}}     # optional, [true | false]
    source_table: {{String}}                    # optional, one of the table name under `tables`
```

<br />

### Fields
Expect at least one field. 

```yaml
fields:
    <field_name_1>: {{Field}}
    <field_name_2>: {{Field}}
    <field_name_3>: {{Field}}
}
```

<br />

### Table
Bracket notation is used to indicate that the table name is a placeholder and should be replaced with the actual table name. The table name should be unique within the `tables`.
```yaml
<table_name>:
    table_id: {{String}}           # mandatory, unique table id copied from Ragic
    fields: {{Fields}}             # mandatory
    sub_tables: [                  # optional, list of sub tables with at least one sub table
        {{String}}              
    ]
```

<br />

### Tables
Expect at least one table.
```yaml
tables:
    <table_name_1>: {{Table}}
    <table_name_2>: {{Table}}
    <table_name_3>: {{Table}}
```

<br />

### Tab
Bracket notation is used to indicate that the tab name is a placeholder and should be replaced with the actual tab name. The tab name should be unique within the `tabs`.

```yaml
tabs:
    <tab_name_1>:
        tab_id: {{String}}
        tables: {{Tables}}
    }

    <tab_name_1>:
        tab_id: {{String}}
        tables: {{Tables}}
    }
```

<br />

# Example

## Sales Management System
```yaml
tabs:
    Sales Management System:
        tab_id: 7
        tables:
            customer:
                table_id: 1
                fields:
                    customer_id:
                        field_id: 1009788
                        field_type: text

                    name:
                        field_id: 1009789
                        field_type: text

                    gender:
                        field_id: 1009790
                        field_type: selection
                        allow_user_add_new_options: false

                    email:
                        field_id: 1009791
                        field_type: text:email

            sales:
                table_id: 2
                fields:
                    product_id:
                        field_id: 1009792
                        field_type: selection
                        allow_user_add_new_options: true
                        source_table: customer

                    quantity:
                        field_id: 1009793
                        field_type: number

                    discount:
                        field_id: 1009794
                        field_type: number

                    total_price:
                        field_id: 1009795
                        field_type: number

                    customer_id:
                        field_id: 1009796
                        field_type: text
                        source_table: customer

            product:
                table_id: 3
                fields:
                    product_id:
                        field_id: 1009797
                        field_type: text
                        
                    product_name:
                        field_id: 1009798
                        field_type: text

                    product_price:
                        field_id: 1009799
                        field_type: number

                    product_description:
                        field_id: 1009800
                        field_type: rich text

                    product_category:
                        field_id: 1009801
                        field_type: multiple select
                        allow_user_add_new_options: true
```
