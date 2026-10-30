# src/data_validator.py
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    for column in required_columns:
        if column not in df.columns:
            logger.error("Required column missing: %s", column)
            raise ValueError(f"Required column missing: {column}")

    invalid_rows = set()

    for col in numeric_columns:
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except (ValueError, TypeError):
                    invalid_rows.add(i)

    if invalid_rows:
        logger.warning(
            "Removed %d rows with invalid numeric values",
            len(invalid_rows)
        )
        df = df.drop(index=list(invalid_rows))

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col])

    logger.debug(
        "Validation: %d -> %d rows",
        len(df) + len(invalid_rows),
        len(df)
    )

    return df