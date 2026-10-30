# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)

    df = df.drop_duplicates()

    rows_after = len(df)
    rows_removed = rows_before - rows_after

    logger.debug(
        "remove_duplicates: %d → %d rows",
        rows_before,
        rows_after
    )

    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        before = len(df)
        df = df.dropna()
        after = len(df)

        logger.debug(
            "handle_missing: %d → %d rows",
            before,
            after
        )

    elif axis == "columns":
        before = len(df.columns)
        df = df.dropna(axis="columns")
        after = len(df.columns)

        logger.debug(
            "handle_missing: %d → %d columns",
            before,
            after
        )

    else:
        logger.error("Unsupported missing value axis: %s", axis)
        raise ValueError(f"Unsupported axis: {axis}")

    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ["iqr", "zscore"]:
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    for column in columns:
        if column not in df.columns:
            logger.warning("Column not found: %s", column)
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        rows_before = len(df)

        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            df = df[
                (df[column] >= lower) &
                (df[column] <= upper)
                ]

            rows_removed = rows_before - len(df)

            logger.debug(
                "%s: lower=%s, upper=%s, removed=%d",
                column,
                lower,
                upper,
                rows_removed
            )

        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()

            if std == 0:
                continue

            z_scores = (df[column] - mean) / std

            df = df[abs(z_scores) <= threshold]

            rows_removed = rows_before - len(df)

            logger.debug(
                "%s: threshold=%s, removed=%d",
                column,
                threshold,
                rows_removed
            )

    return df


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]

    if processing["remove_duplicates"]:
        df = remove_duplicates(df)

    if processing["missing"]["enabled"]:
        axis = processing["missing"]["axis"]
        df = handle_missing(df, axis)

    if processing["outliers"]["enabled"]:
        columns = processing["outliers"]["columns"]
        method = processing["outliers"]["method"]
        threshold = processing["outliers"]["threshold"]

        df = remove_outliers(
            df,
            columns,
            method,
            threshold
        )

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = len(df_before)
    rows_after = len(df_after)

    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after
    }
