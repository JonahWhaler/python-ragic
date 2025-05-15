# import os
import json
import logging
from dotenv import load_dotenv

# import pandas as pd
from ragic import (
    RagicAPIClient,
    OperandType,
    Ordering,
    OrderingType,
    OtherGETParameters,
)


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        filename=r"./logs/ragic.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    client = RagicAPIClient(
        base_url=None,
        namespace=None,
        api_key=None,
        version=3,
        structure_path="structure.yaml",
    )

    TAB_NAME = "PB"
    TABLE_NAME = "Donations"
    # [("Race", OperandType.EQUALS, "Others")]
    data_dict = client.load(
        TAB_NAME,
        TABLE_NAME,
        conditions=None,
        offset=0,
        size=10,
        other_get_params=OtherGETParameters(subtables=False, listing=False),
        ordering=Ordering(order_by="ID", order=OrderingType.ASC),
    )

    if data_dict:
        with open(r"./output/data.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(data_dict, ensure_ascii=False, indent=4))
    else:
        logger.info("No data found.")
