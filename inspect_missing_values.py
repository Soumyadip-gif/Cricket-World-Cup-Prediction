from src.data.data_loader import load_all_datasets

datasets = load_all_datasets()

for name, df in datasets.items():
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print(f"\n--- {name.upper()} ---")

    if missing.empty:
        print("No missing values.")
    else:
        for column, count in missing.items():
            percentage = count / len(df) * 100
            print(f"{column}: {count} ({percentage:.2f}%)")
