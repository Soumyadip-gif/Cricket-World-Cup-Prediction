
import logging

import pandas as pd

from config import (
    ODI_DATASET,
    T20_DATASET,
    COMBINED_DATASET,
    PREDICTION_DATASET,
    TRAINING_DATASET,
    VALIDATION_DATASET,
    TEST_DATASET,
)

logger = logging.getLogger(__name__)

DATASET_PATHS = {
    "odi": ODI_DATASET,
    "t20": T20_DATASET,
    "combined": COMBINED_DATASET,
    "prediction": PREDICTION_DATASET,
    "training": TRAINING_DATASET,
    "validation": VALIDATION_DATASET,
    "test": TEST_DATASET,
}

REQUIRED_COLUMNS = {
    "odi": {"YEAR", "FORMAT", "TEAM1", "TEAM2", "WINNER", "VENUE"},
    "t20": {"YEAR", "FORMAT", "TEAM1", "TEAM2", "WINNER", "VENUE"},
    "combined": {"YEAR", "FORMAT", "TEAM1", "TEAM2", "WINNER", "VENUE"},
    "prediction": {"FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE", "TEAM1_WIN"},
    "training": {"FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE", "TEAM1_WIN"},
    "validation": {"FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE", "TEAM1_WIN"},
    "test": {"FORMAT", "YEAR", "TEAM1", "TEAM2", "VENUE", "TEAM1_WIN"},
}


def load_dataset(name):
    """Load and validate an existing dataset."""

    if name not in DATASET_PATHS:
        raise ValueError(f"Unknown dataset: {name}")

    path = DATASET_PATHS[name]

    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    try:
        dataframe = pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeError) as exc:
        logger.exception("Failed to read dataset: %s", name)
        raise RuntimeError(
            f"Unable to read dataset '{name}': {exc}"
        ) from exc

    missing = REQUIRED_COLUMNS[name] - set(dataframe.columns)

    if missing:
        raise ValueError(
            f"Dataset '{name}' is missing columns: {sorted(missing)}"
        )

    logger.info(
        "Loaded dataset '%s': %s rows, %s columns",
        name,
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe


def load_all_datasets():
    """Load all seven existing datasets."""

    return {
        name: load_dataset(name)
        for name in DATASET_PATHS
    }


def get_dataset_summary(datasets):
    """Return basic dataset information."""

    summary = []

    for name, dataframe in datasets.items():
        summary.append({
            "dataset": name,
            "records": len(dataframe),
            "columns": len(dataframe.columns),
        })

    return pd.DataFrame(summary)
