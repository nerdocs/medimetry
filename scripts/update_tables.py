#
# This script downloads WHO child growth data from the World Health Organization (WHO)
# and converts them to a CSV format
#
# Sources:
# https://cdn.who.int/media/docs/default-source/child-growth/child-growth
# -standards/indicators/{pattern}/{expanded-tables|expandable-tables}/{abbrev,
# e.g. lhfa}-{girls|boys}-{percentiles|zscore}-expanded-tables.xlsx
from pathlib import Path

import pandas as pd
import requests

# lhfa lives in "expandable-tables" directory at WHO's, the others in
# "expanded-tables"...
patterns = [
    ("lhfa", "length-height-for-age", "expandable-tables"),
    ("wfa", "weight-for-age", "expanded-tables"),
    ("wfh", "weight-for-length-height", "expanded-tables"),
    ("hcfa", "head-circumference-for-age", "expanded-tables"),
    ("bfa", "body-mass-index-for-age", "expanded-tables"),
]

genders = ["girls", "boys"]

data_types = ["percentiles", "zscore"]

target_directory = "src/medimetry/data/anthropometric"


def download_who_data():
    """Download WHO child growth data files."""
    base_url = "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators"

    # get the base directory of medimetry package - we are in scripts/
    base_dir = Path(__file__).parent.parent

    for abbrev, pattern, buggy_expand_name in patterns:
        for gender in genders:
            for data_type in data_types:
                # Construct URL
                filename = f"{abbrev}-{gender}-{data_type}-expanded-tables.xlsx"
                url = f"{base_url}/{pattern}/{buggy_expand_name}/{filename}"

                # Download file
                print(f"Downloading {filename}...")
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code != 200:
                        response.raise_for_status()

                    # Save to current directory
                    filepath = base_dir / target_directory / filename
                    with Path.open(filepath, "wb") as f:
                        f.write(response.content)

                    print(f"✓ Downloaded {filename}")

                    # Convert to CSV
                    csv_filename = filename.replace(".xlsx", ".csv")
                    csv_filepath = base_dir / target_directory / csv_filename

                    print(f"Converting {filename} to CSV...")
                    try:
                        df = pd.read_excel(filepath)
                        df.to_csv(csv_filepath, sep=";", index=False)
                        print(f"✓ Converted to {csv_filename}")
                        # we can delete the xlsx file now
                        filepath.unlink()
                    except Exception as e:
                        print(f"✗ Failed to convert {filename} to CSV: {e}")

                except requests.exceptions.RequestException as e:
                    print(f"✗ Failed to download {filename}: {e}")


if __name__ == "__main__":
    download_who_data()
