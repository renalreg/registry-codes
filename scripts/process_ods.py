import pandas as pd
from pathlib import Path


gp_codes_path = Path("tables") / "ukrdc_ods_gp_codes" / "egpcur.csv"
practice_codes_path = Path("tables") / "ukrdc_ods_gp_codes" / "epraccur.csv"

practice_codes_df = pd.read_csv(practice_codes_path, header=None)
gp_codes_df = pd.read_csv(gp_codes_path, header=None)


# Future Note: colums 4-8 should probably be concatenated

gp_codes_df = gp_codes_df.iloc[:, [0, 1, 4, 9, 17]]
gp_codes_df.loc[:, "type"] = "GP"


practice_codes_df = practice_codes_df.iloc[:, [0, 1, 4, 9, 17]]
practice_codes_df.loc[:, "type"] = "PRACTICE"


# Concatinate and save in the same directory as gp_and_prac_ods.csv then delete originals
gp_and_practice_codes_df = pd.concat(
    [gp_codes_df, practice_codes_df], ignore_index=True
)

# Truncate strings to 50 and 35 characters
gp_and_practice_codes_df.iloc[:, 1] = gp_and_practice_codes_df.iloc[:, 2].apply(
    lambda x: x[:50] if len(x) > 50 else x
)
gp_and_practice_codes_df.iloc[:, 2] = gp_and_practice_codes_df.iloc[:, 3].apply(
    lambda x: x[:35] if len(x) > 35 else x
)

gp_and_practice_codes_filepath = (
    Path("tables") / "ukrdc_ods_gp_codes" / "gp_and_prac_ods.csv"
)
gp_and_practice_codes_df.to_csv(
    gp_and_practice_codes_filepath, index=False, header=False
)
gp_codes_path.unlink()
practice_codes_path.unlink()
