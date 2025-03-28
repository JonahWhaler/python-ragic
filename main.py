import os
import logging
from dotenv import load_dotenv
import pandas as pd
from ragic import DataClient, QueryFilterType


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        filename="./logs/ragic.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    client = DataClient(
        base_url=os.environ.get("RAGIC_URL"),
        namespace=os.environ.get("RAGIC_NAMESPACE"),
        api_key=os.environ.get("RAGIC_API_KEY"),
        version=3,
        structure_path="./config/structure.yaml",
    )
    # Parameters
    TAB_NAME = "##"
    TABLE_NAME = "##"
    conditions = [
        ("FIELD 1", QueryFilterType.CONTAINS, "FIELD VALUE 1"),
        ("FIELD 2", QueryFilterType.EQUAL, "FIELD VALUE 2"),
    ]
    offset = 0
    LIMIT = 1000
    collected_rows = 0
    main_df = pd.DataFrame()
    try:
        while True:
            # time.sleep(0.2)  # Prevent Rate Limit
            client.define_query(
                tab_name=TAB_NAME,
                table_name=TABLE_NAME,
                conditions=conditions,
                offset=offset,
                limit=LIMIT,
            )
            df = client.get_dataframe()
            if df is not None and df.shape[0] > 0:
                main_df = pd.concat([main_df, df], axis=0, ignore_index=True)
                # df.info()
                collected_rows += df.shape[0]
                logger.info("Total rows collected: %s", collected_rows)
                offset += LIMIT
            else:
                break
        main_df.info()
        main_df.to_csv("./output.csv", index=False)
    except Exception as e:
        logger.error("Main loop error: %s", e)
        logger.warning("Offset: %s", offset)
