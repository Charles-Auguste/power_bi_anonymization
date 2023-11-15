# Library
import io
import json
import re
import zipfile
from pathlib import Path
from pprint import pprint
from typing import Dict, List

import pandas as pd
import streamlit as st
from powerbi_anonymisation_pkg.anonymise import anonymise_cat, anonymise_float


def uploader():
    st.header("1) Upload Data")
    uploaded_files = st.file_uploader("", accept_multiple_files=True)
    list_df = []
    dict_parameters = {}
    st.session_state["cache_configuration"] = {}
    if uploaded_files:
        for idx_file, file in enumerate(uploaded_files):
            st.subheader(Path(file.name).stem)
            if Path(file.name).suffix == ".xlsx":
                list_sheets = pd.ExcelFile(file).sheet_names
                dict_parameters[f"sheet_{idx_file}"] = st.selectbox(
                    "Sheet", list_sheets, key=f"sheet_{idx_file}"
                )
                # Read excel
                st.write("Preview")
                try:
                    df = pd.read_excel(
                        file, sheet_name=dict_parameters[f"sheet_{idx_file}"]
                    )
                    st.dataframe(df.head())
                except Exception as e:
                    df = pd.DataFrame()
                    st.write(f"Cannot open your file : {str(e)}")

                list_df.append(
                    {
                        "name": Path(file.name).stem,
                        "df": df,
                        "transco": {},
                        "new_df": pd.DataFrame(),
                    }
                )

            elif Path(file.name).suffix == ".csv":
                list_encoding = ("utf-16", "latin-1", "utf-8")
                list_sep = (";", ",", "|")
                col1, col2 = st.columns(2)
                with col1:
                    dict_parameters[f"sep_{idx_file}"] = st.selectbox(
                        "Separator", list_sep, key=f"sep_{idx_file}"
                    )

                with col2:
                    dict_parameters[f"encode_{idx_file}"] = st.selectbox(
                        "Encoding", list_encoding, key=f"encode_{idx_file}"
                    )

                # Read .csv
                st.write("Preview")
                try:
                    df = pd.read_csv(
                        file,
                        sep=dict_parameters[f"sep_{idx_file}"],
                        encoding=dict_parameters[f"encode_{idx_file}"],
                    )
                    st.dataframe(df.head())
                except Exception as e:
                    df = pd.DataFrame()
                    st.write(f"Cannot open your file : {str(e)}")

                list_df.append(
                    {
                        "name": Path(file.name).stem,
                        "df": df,
                        "transco": {},
                        "new_df": pd.DataFrame(),
                    }
                )
            elif Path(file.name).suffix == ".json":
                print("Loading a configuration file")
                text_json = file.read().decode("utf-8")
                possible_configuration = json.loads(text_json)
                print(possible_configuration)
                st.session_state["cache_configuration"] = possible_configuration

            else:
                list_df.append(
                    {
                        "name": Path(file.name).stem,
                        "df": pd.DataFrame(),
                        "transco": {},
                        "new_df": pd.DataFrame(),
                    }
                )

        st.info(
            "Be sure that all of your tables have been loaded. Otherwise you won't be able do use them or their columns. Sometimes, you will just have to switch between UTF15 and UTF8 encoding"  # noqa
        )

        return list_df


def check_if_configuration_valid(
    possible_config,
    list_df,
):
    print("#########")
    print(possible_config)
    print("#########")
    if len(possible_config) == 0:
        st.warning("No configuration file detected. Have you uploaded it ?")
        return False
    # Check if all dataframes are here
    list_df_names = set([el["name"] for el in list_df])
    list_config_names = set(possible_config.keys())
    if len(list_df_names - list_config_names) > 0:
        st.warning(
            f"Cannot load your configuration, \
            some tables are missing in the configuration: {list_df_names - list_config_names}"  # noqa
        )
        return False
    if len(list_config_names - list_df_names) > 0:
        st.warning(
            f"Cannot load your configuration, \
            some tables are missing in the uploader: {list_config_names - list_df_names}"  # noqa
        )
        return False
    # Check for each tables columns names
    dict_columns = {el["name"]: list(el["df"].columns) for el in list_df}
    for key in possible_config.keys():
        for column_key in possible_config[key]:
            column_concerned = column_key["name"]
            if column_concerned != "" and column_concerned not in dict_columns[key]:
                st.warning(
                    f"Cannot load your configuration, \
                    a column is missing in : {column_concerned}"
                )
                return False

        return True


def modify_view(list_df):
    st.header("2) Modify Data")

    st.info(
        "Please download you configuration if you want to save your work. Next time, just upload your .json file with the rest of the excels"  # noqa
    )

    # Define a template dict element
    template_dict_el = {
        "name": "",
        "type": "Category",
        "coeff": "",
        "is_link": "No",
        "alias": "",
        "link_name": "",
        "link_field": "",
    }

    # Save the result dictionnary in cache
    if "cache_dict_of_orders" not in st.session_state:
        dict_of_orders = {el["name"]: [template_dict_el.copy()] for el in list_df}
        st.session_state["cache_dict_of_orders"] = dict_of_orders
    else:
        dict_of_orders = st.session_state["cache_dict_of_orders"]

    col_config1, col_config2, col_config3 = st.columns([2, 2, 10])
    with col_config1:
        json_string = json.dumps(dict_of_orders, ensure_ascii=False)
        st.download_button(
            label="Download configuration",
            file_name="config.json",
            mime="application/json",
            data=json_string,
        )

    with col_config2:
        if st.button("Load configuration"):
            if check_if_configuration_valid(
                st.session_state["cache_configuration"],
                list_df,
            ):
                dict_of_orders = st.session_state["cache_configuration"]
                st.session_state["cache_dict_of_orders"] = dict_of_orders

    # Loop over dataset of list_df
    for idx_df, df_dict in enumerate(list_df):
        # Get data about the dataframe
        table_name = df_dict["name"]
        df_columns = list(df_dict["df"].columns)
        print("\n\n")
        print("#### Table name :", table_name)
        print("#### Table columns :", df_columns)

        # Check if a version of the dataset configuration is stored in Cache
        # If no, create a new entry
        if table_name not in dict_of_orders:
            dict_of_orders[table_name] = [template_dict_el]

        # Read the number of configuration rows linked with the dataset
        nb_row = len(dict_of_orders[table_name])
        print("#### Number of configuration rows :", nb_row)

        st.subheader(table_name)

        # Loop over those rows
        for row_index in range(nb_row):
            print("-" * 40)
            print("#### Row number :", row_index)
            print("#### Configuration dictionnary :")
            pprint(dict_of_orders[table_name][row_index])
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            # Column 1: Choose the column to anonymise
            with col1:
                dict_of_orders[table_name][row_index]["name"] = st.selectbox(
                    "Select a column",
                    (df_columns + [""]),
                    index=(df_columns + [""]).index(
                        dict_of_orders[table_name][row_index]["name"]
                    ),
                    key=f"COLUMN_file_{idx_df}_row_{row_index}",
                )

            # Column 2: Select the type of anonymisation (Category or Numeric)
            with col2:
                dict_of_orders[table_name][row_index]["type"] = st.selectbox(
                    "Type",
                    ["Category", "Numeric"],
                    index=["Category", "Numeric"].index(
                        dict_of_orders[table_name][row_index]["type"]
                    ),
                    key=f"TYPE_file_{idx_df}_row_{row_index}",
                )

            # Column 3:
            with col3:
                # If Numeric, write the coefficient or the range
                if dict_of_orders[table_name][row_index]["type"] == "Numeric":
                    dict_of_orders[table_name][row_index]["coeff"] = st.text_input(
                        "Coefficient or range ([xx.xx, xx.xx])",
                        value=dict_of_orders[table_name][row_index]["coeff"],
                        key=f"COEFF_file_{idx_df}_row_{row_index}",
                    )

                # If Category, write if a possible join must be considered
                else:
                    dict_of_orders[table_name][row_index]["is_link"] = st.selectbox(
                        "Link with other table ?",
                        ["Yes", "No"],
                        index=["Yes", "No"].index(
                            dict_of_orders[table_name][row_index]["is_link"]
                        ),
                        key=f"LINK_file_{idx_df}_row_{row_index}",
                    )

            # Column 4:
            with col4:
                if dict_of_orders[table_name][row_index]["type"] != "Numeric":
                    # If the dataset must be merge, choose destination dataset
                    if dict_of_orders[table_name][row_index]["is_link"] == "Yes":
                        dict_of_orders[table_name][row_index][
                            "link_name"
                        ] = st.selectbox(
                            "Source Table",
                            [el["name"] for el in list_df if el["name"] != table_name]
                            + [""],
                            index=(
                                [
                                    el["name"]
                                    for el in list_df
                                    if el["name"] != table_name
                                ]
                                + [""]
                            ).index(dict_of_orders[table_name][row_index]["link_name"]),
                            key=f"TABLE_file_{idx_df}_row_{row_index}",
                        )

                    # If no merge, then choose the alias for anonymisation
                    else:
                        dict_of_orders[table_name][row_index]["alias"] = st.text_input(
                            "Alias",
                            value=dict_of_orders[table_name][row_index]["alias"],
                            key=f"ALIAS_file_{idx_df}_row_{row_index}",
                        )

            # Column 5: Choose destination column if merge
            with col5:
                if dict_of_orders[table_name][row_index]["type"] != "Numeric":
                    if dict_of_orders[table_name][row_index]["is_link"] == "Yes":
                        if dict_of_orders[table_name][row_index]["link_name"] != "":
                            list_columns = [
                                list(el["df"].columns)
                                for el in list_df
                                if el["name"]
                                == dict_of_orders[table_name][row_index]["link_name"]
                            ]
                            try:
                                dict_of_orders[table_name][row_index][
                                    "link_field"
                                ] = st.selectbox(
                                    "Source Column",
                                    list_columns[0] + [""],
                                    index=(list_columns[0] + [""]).index(
                                        dict_of_orders[table_name][row_index][
                                            "link_field"
                                        ]
                                    ),
                                    key=f"COLUMN_LINK_file_{idx_df}_row_{row_index}",
                                )
                            except ValueError:
                                dict_of_orders[table_name][row_index][
                                    "link_field"
                                ] = st.selectbox(
                                    "Source Column",
                                    list_columns[0] + [""],
                                    index=len(list_columns[0] + [""]) - 1,
                                    key=f"COLUMN_LINK_file_{idx_df}_row_{row_index}",
                                )

            # Column 6: Delete row button
            with col6:
                st.write("##")
                if st.button("Delete row", key=f"DEL_file_{idx_df}_row_{row_index}"):
                    del dict_of_orders[table_name][row_index]
                    st.session_state["cache_dict_of_orders"] = dict_of_orders
                    st.experimental_rerun()

        # Add a "add new line" button
        if st.button("Add a new line", key=f"ADD_file_{idx_df}"):
            dict_of_orders[table_name].append(template_dict_el)
            st.session_state["cache_dict_of_orders"] = dict_of_orders
            st.experimental_rerun()

    return dict_of_orders


def is_float_or_range(
    number: str,
):
    try:
        float(number)
        return True
    except ValueError:
        try:
            find = re.search(r"\[([\d\.]*),([\d\.]*)\]", number)
            float(find.group(1))
            float(find.group(2))
            return True
        except Exception as e:
            print(str(e))
            return False


def is_column_spec_correct(
    column_info: Dict,
):
    # Check if name
    if column_info["name"].strip() == "":
        st.write("-  Warning : A column name wasn't completed")
        return False

    # Numeric columns
    if column_info["type"] == "Numeric":
        # Check range or coeff
        if not is_float_or_range(column_info["coeff"]):
            st.write(
                f"-  Warning : For column {column_info['name']}, \
                there are some issues with the coefficient"
            )
            return False

    # Categorical columns
    elif column_info["type"] == "Category":
        # Without link
        if column_info["is_link"] == "No":
            if column_info["alias"].strip() == "":
                st.write(
                    f"-  Warning : For column {column_info['name']}, \
                    no alias was specified"
                )
                return False
        # With link
        else:
            if (
                column_info["link_name"].strip() == ""
                or column_info["link_field"].strip() == ""
            ):
                st.write(
                    f"-  Warning : For column {column_info['name']}, \
                    there are some issues with linked table"
                )
                return False

    # Without previous error... Ok !
    st.write(f"-  Info : Correct inputs for column {column_info['name']}")
    return True


def modify_execute(list_df: List, dict_df: Dict):
    st.header("3) Anonymise...")
    ok_anonymise = st.button("Compute new tables", key="compute_anonymise")
    list_order = []
    if ok_anonymise:
        # List of checks
        # --------------
        # Basic checks
        for key in dict_df.keys():
            st.write(f"{key}")
            list_all_columns = []
            for col in dict_df[key]:
                if col["name"] in list_all_columns:
                    st.write(f"-  Warning : More than one config row for {col['name']}")
                elif is_column_spec_correct(col):
                    col.update({"file": key})
                    list_order.append(col)
                    list_all_columns.append(col["name"])
        # Circular link checks
        circular_checks = []
        for order in list_order:
            if order["is_link"] == "Yes":
                link = (
                    order["file"].strip()
                    + "_"
                    + order["name"].strip()
                    + "||"
                    + order["link_name"].strip()
                    + "_"
                    + order["link_field"].strip()
                )
                link_reverse = (
                    order["link_name"].strip()
                    + "_"
                    + order["link_field"].strip()
                    + "||"
                    + order["file"].strip()
                    + "_"
                    + order["name"].strip()
                )
                if link in circular_checks or link_reverse in circular_checks:
                    st.error(
                        "A circular import has been detected, please checks your links"
                    )
                    return
                else:
                    circular_checks.append(link)
                    circular_checks.append(link_reverse)

        # Transform into a readable list of orders
        # ----------------------------------------
        for idx, order in enumerate(list_order):
            # Numeric
            if order["type"] == "Numeric":
                try:
                    order["coefficient"] = float(order["coeff"])
                except ValueError:
                    find = re.search(r"\[([\d\.]*),([\d\.]*)\]", order["coeff"])
                    value_1 = float(find.group(1))
                    value_2 = float(find.group(2))
                    order["coefficient"] = [
                        min(value_1, value_2),
                        max(value_1, value_2),
                    ]

        # Sort list for the links
        # -----------------------
        # 1) Numeric orders
        # 2) Categorical without links orders
        # 3) Linked orders
        list_numeric_orders = []
        list_simple_category_orders = []
        list_complex_category_orders = []

        for order in list_order:
            if order["type"] == "Numeric":
                list_numeric_orders.append(order)
            elif order["type"] == "Category" and order["is_link"] == "No":
                list_simple_category_orders.append(order)
            elif order["type"] == "Category" and order["is_link"] == "Yes":
                list_complex_category_orders.append(order)
            else:
                pass

        # Anonymize
        # ---------
        for idx_df, df_dict in enumerate(list_df):
            list_df[idx_df]["new_df"] = list_df[idx_df]["df"].copy()

        for order in list_numeric_orders:
            name = order["file"]
            coeff = order["coefficient"]
            col_name = order["name"]
            idx_df = [idx for idx, el in enumerate(list_df) if el["name"] == name][0]
            list_df[idx_df]["new_df"] = anonymise_float(
                list_df[idx_df]["new_df"],
                col_name,
                coeff,
            )

        for order in list_simple_category_orders:
            name = order["file"]
            alias = order["alias"]
            col_name = order["name"]
            idx_df = [idx for idx, el in enumerate(list_df) if el["name"] == name][0]
            (
                list_df[idx_df]["new_df"],
                list_df[idx_df]["transco"][col_name],
            ) = anonymise_cat(
                list_df[idx_df]["new_df"],
                col_name,
                alias,
            )

        for order in list_complex_category_orders:
            name = order["file"]
            col_name = order["name"]
            other_table = order["link_name"]
            other_column = order["link_field"]
            idx_df = [idx for idx, el in enumerate(list_df) if el["name"] == name][0]
            idx_other_df = [
                idx for idx, el in enumerate(list_df) if el["name"] == other_table
            ][0]
            transco_table = list_df[idx_other_df]["transco"].get(
                other_column, pd.DataFrame()
            )
            if transco_table.shape[0] > 0:
                (
                    list_df[idx_df]["new_df"],
                    list_df[idx_df]["transco"][col_name],
                ) = anonymise_cat(
                    list_df[idx_df]["new_df"],
                    col_name,
                    transco_table,
                )
                list_df[idx_other_df]["transco"][other_column] = list_df[idx_df][
                    "transco"
                ][col_name]

        # Print Result
        for df in list_df:
            st.subheader(df["name"])
            st.dataframe(df["new_df"].head())

        return list_df


def download(list_df):
    st.header("4) Download")
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "x") as csv_zip:
        for df in list_df:
            csv_zip.writestr(
                f"{df['name']}.csv",
                df["new_df"].to_csv(index=False, encoding="latin-1", sep=";"),
            )

    st.download_button(
        label="Download zip",
        data=buf.getvalue(),
        file_name="anonymise_data.zip",
        mime="application/zip",
    )


def app():
    st.set_page_config(layout="wide")
    st.title("Power Bi Anonymisation Tool")
    list_df = uploader()
    if list_df:
        list_df = [el for el in list_df if not el["df"].empty]
        dict_df = modify_view(list_df)
        continue_compute = False
        for key in dict_df.keys():
            list_columns = dict_df[key]
            if len([el["name"] for el in list_columns if el["name"] != ""]) > 0:
                continue_compute = True
        if continue_compute:
            list_df = modify_execute(
                list_df,
                dict_df,
            )

            if list_df:
                download(list_df)


# Main script
if __name__ == "__main__":
    app()
