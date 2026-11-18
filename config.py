
from pathlib import Path


# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Existing historical dataset directory
SOURCE_DATA_DIR = Path(
    r"C:\Users\HP\Documents\Cricket_datset\processed"
)

# Application directories
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
LOG_DIR = BASE_DIR / "logs"
INSTANCE_DIR = BASE_DIR / "instance"


# Existing datasets
ODI_DATASET = SOURCE_DATA_DIR / "ODI_World_Cup_Master_Dataset.csv"

T20_DATASET = SOURCE_DATA_DIR / "T20_World_Cup_Master_Dataset.csv"

COMBINED_DATASET = (
    SOURCE_DATA_DIR / "Combined_Cricket_World_Cup_Master_Dataset.csv"
)

PREDICTION_DATASET = (
    SOURCE_DATA_DIR / "Prediction_Ready_Dataset.csv"
)

TRAINING_DATASET = SOURCE_DATA_DIR / "Model_Training_Data.csv"

VALIDATION_DATASET = SOURCE_DATA_DIR / "Model_Validation_Data.csv"

TEST_DATASET = SOURCE_DATA_DIR / "Model_Test_Data.csv"


# Existing baseline model
BASELINE_MODEL = (
    SOURCE_DATA_DIR / "Cricket_World_Cup_Prediction_Model.pkl"
)


# Application settings
APP_NAME = "Cricket World Cup Match Prediction System"

APP_VERSION = "1.0.0"

DEBUG = True
