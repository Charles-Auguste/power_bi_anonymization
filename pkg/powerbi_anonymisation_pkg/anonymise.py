# Library
import random
from typing import List, Tuple, Union

import pandas as pd
from termcolor import colored


def anonymise_cat(
    df: pd.DataFrame,
    col_name: str,
    alt: Union[pd.DataFrame, str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Anonymise a categorical column

    Parameters
    ----------
        df: pd.DataFrame
            Input DataFrame with the column to anonymise

        col_name: str
            Name of the column to anonymise

        alt: str or pd.DataFrame
            if str, the name of alternative data to create. For example,
            if alt = "CLIENT", data will be replaced with
            CLIENT_1, CLIENT_2, etc ....

            if pd.DataFrame, the daatframe must be the merge key with another field.
            For example, if two columns related to customers are meant to be merged
            between table A and B, then after the anonymisation of customer field
            in table A, one gets a transcoding table to use as an alt parameter
            for table B

    Returns
    -------
        df: pd.DataFrame
            The previous dataframe with the column col_name anonymised

        df_to_merge: pd.DataFrame
            The transcoding table between col_name's elements and the new anonymised
            words
    """
    print(colored(f"Anonymise category for column {col_name}", "green"))
    print("")
    if isinstance(alt, str):
        # If alt value is a string --> create a transcoding table
        # -------------------------------------------------------
        col_values = df[col_name].value_counts()
        alternative_values = [f"{alt} {i}" for i in range(1, col_values.shape[0] + 1)]
        df_to_merge = pd.DataFrame()
        df_to_merge["before"] = list(col_values.index)
        df_to_merge["after"] = alternative_values

    else:
        # If alt value is a dataframe --> update the current transcoding table
        # --------------------------------------------------------------------
        col_values = list(df[col_name].value_counts().index)
        new_before = pd.DataFrame()
        new_before["before"] = col_values
        df_to_merge = pd.merge(alt, new_before, on="before", how="outer")
        # get alt str info : Name and Max now
        df_to_merge["test_name"] = (
            df_to_merge["after"].str.rsplit(n=1).str[0].astype(str)
        )
        df_to_merge["test_value"] = (
            df_to_merge["after"].str.rsplit(n=1).str[1].astype(str)
        )
        last_value = (
            df_to_merge.loc[df_to_merge.test_value.str.isdigit(), "test_value"]
            .astype(int)
            .max()
        )
        print(colored(last_value, "red"))
        print(df_to_merge)
        print(colored("=" * 20, "red"))
        name = str(df_to_merge.loc[0, "test_name"]).strip()
        nb_row_to_add = df_to_merge[df_to_merge.after.isna()].shape[0]
        list_to_add = [
            f"{name} {i}" for i in range(last_value + 1, last_value + 1 + nb_row_to_add)
        ]
        df_to_merge.loc[df_to_merge.after.isna(), "after"] = list_to_add
        df_to_merge = df_to_merge[["before", "after"]]

    # Update the columns data according to the transcoding table
    # ----------------------------------------------------------
    df = pd.merge(
        df, df_to_merge, left_on=col_name, right_on="before", how="left", validate="m:1"
    )
    df.drop([col_name, "before"], axis=1, inplace=True)
    df.rename(
        columns={
            "after": col_name,
        },
        inplace=True,
    )

    return (df, df_to_merge)


def anonymise_float(
    df: pd.DataFrame,
    col_name: str,
    range_values: Union[List, float],
    decimal_nb: int = 2,
) -> pd.DataFrame:
    """
    Anonymise a numerical column

    Parameters
    ----------
        df: pd.DataFrame
            Input DataFrame with the column to anonymise

        col_name: str
            Name of the column to anonymise

        range_values: List or float
            If float, the factor that will be multiplied with df column's fields

            If List, the interval in which a random float is chosen as the
            multiplication factor

    Returns
    -------
        df: pd.DataFrame
            The previous dataframe with the column col_name anonymised
    """
    print(colored(f"Anonymise float for column {col_name}", "yellow"))
    # Transform the column into a fully readable one by python
    # --------------------------------------------------------
    df[col_name] = df[col_name].astype(str).str.replace(",", ".")
    df[col_name] = pd.to_numeric(df[col_name], downcast="float", errors="coerce")
    if isinstance(range_values, float):
        # if float --> update df with a simple multiplication
        # ---------------------------------------------------
        df[col_name] = df[col_name] * range_values
        df[col_name] = df[col_name].round(decimal_nb)

    else:
        # If range --> find uniformaly a factor in the interval and then multiply it
        # --------------------------------------------------------------------------
        min_range, max_range = range_values[0], range_values[1]
        coeff = random.uniform(min_range, max_range)
        df[col_name] = df[col_name] * coeff
        df[col_name] = df[col_name].round(decimal_nb)

    # Transform the column into a fully readable one by excel
    # -------------------------------------------------------
    df[col_name] = df[col_name].astype(str).str.replace(".", ",")

    return df
