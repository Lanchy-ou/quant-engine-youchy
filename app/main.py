import pandas as pd
from pathlib import Path

def main():
    print("Project bootstrapped successfully")

    data_path = Path("data/sample_data.csv")
    if data_path.exists():
        df = pd.read_csv(data_path)
        print("sample data loaded:")
        print(df.head())
    else:
        print("No sample data found.")

if __name__ == "__main__":
    main()