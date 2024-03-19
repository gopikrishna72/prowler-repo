# Standard library imports
import glob
import importlib
import math
import os
import re
import warnings

# Third-party imports
import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import callback, dcc, html
from dash.dependencies import Input, Output

from dashboard.lib.dropdowns import create_account_dropdown_compliance, create_compliance_dropdown, create_region_dropdown_compliance, create_date_dropdown_compliance
from dashboard.lib.layouts import create_layout_compliance

# Config import
from dashboard.config import folder_path_compliance

# Suppress warnings
warnings.filterwarnings("ignore")

# Global variables
# TODO: Create a flag to let the user put a custom path

csv_files = [file for file in glob.glob(os.path.join(folder_path_compliance, "*.csv"))]


def load_csv_files(csv_files):
    # Load CSV files into a single pandas DataFrame.
    dfs = []
    results = []
    for file in csv_files:
        df = pd.read_csv(file, sep=";", on_bad_lines="skip")
        if "CHECKID" in df.columns and "mitre" not in file.split("/")[-1]:
            dfs.append(df)
            result = file
            result = result.split("/")[-1]
            result = re.sub(r"^.*?_", "", result)
            result = result.replace(".csv", "")
            result = result.upper()
            if "AWS" in result:
                if "AWS_" in result:
                    result = result.replace("_AWS", "")
                else:
                    result = result.replace("_AWS", " - AWS")
            if "GCP" in result:
                result = result.replace("_GCP", " - GCP")
            results.append(result)

    unique_results = set(results)
    results = list(unique_results)

    # Check if there is any CIS report in the list and divide it in level 1 and level 2
    new_results = []
    for compliance_name in results:
        if "CIS_" in compliance_name:
            results.remove(compliance_name)
            new_results.append(compliance_name + " - Level_1")
            new_results.append(compliance_name + " - Level_2")

    results = results + new_results
    results.sort()
    return pd.concat(dfs, ignore_index=True), results


data, results = load_csv_files(csv_files)

data["ASSESSMENTDATE"] = pd.to_datetime(data["ASSESSMENTDATE"])
data["ASSESSMENT_TIME"] = data["ASSESSMENTDATE"].dt.strftime("%Y-%m-%d %H:%M:%S")

data_values = data["ASSESSMENT_TIME"].unique()
data_values.sort()
data_values = data_values[::-1]
aux = []
for value in data_values:
    if value.split(" ")[0] not in [aux[i].split(" ")[0] for i in range(len(aux))]:
        aux.append(value)
data_values = aux

data = data[data["ASSESSMENT_TIME"].isin(data_values)]
data["ASSESSMENT_TIME"] = data["ASSESSMENT_TIME"].apply(lambda x: x.split(" ")[0])

# Select Compliance - Dropdown

compliance_dropdown = create_compliance_dropdown(results)

# Select Account - Dropdown

select_account_dropdown_list = ["All"]
select_account_dropdown_list = (
    select_account_dropdown_list
    + list(data["ACCOUNTID"].unique())
    + list(data["PROJECTID"].unique())
)
list_items = []
for item in select_account_dropdown_list:
    if item.__class__.__name__ == "str":
        list_items.append(item)

account_dropdown = create_account_dropdown_compliance(list_items)

# Select Region - Dropdown

select_region_dropdown_list = ["All"]
select_region_dropdown_list = (
    select_region_dropdown_list
    + list(data["REGION"].unique())
)

list_items = []
for item in select_region_dropdown_list:
    if item.__class__.__name__ == "str":
        list_items.append(item)

region_dropdown = create_region_dropdown_compliance(list_items)

# Dropdown all options
select_date_dropdown_list = list(data["ASSESSMENT_TIME"].unique())

date_dropdown = create_date_dropdown_compliance(select_date_dropdown_list)


dash.register_page(__name__)

layout = create_layout_compliance(account_dropdown, date_dropdown, region_dropdown, compliance_dropdown)

@callback(
    [
        Output("output", "children"),
        Output("overall_status_result_graph", "children"),
        Output("security_level_graph", "children"),
        Output("cloud-account-filter-compliance", "value"),
        Output("cloud-account-filter-compliance", "options"),
        Output("region-filter-compliance", "value"),
        Output("region-filter-compliance", "options"),
        Output("date-filter-analytics", "value"),
        Output("date-filter-analytics", "options"),
    ],
    Input("report-compliance-filter", "value"),
    Input("cloud-account-filter-compliance", "value"),
    Input("region-filter-compliance", "value"),
    Input("date-filter-analytics", "value"),
)
def display_data(
    analytics_input, account_filter, region_filter_analytics, date_filter_analytics
):

    current_compliance = analytics_input
    analytics_input = analytics_input.replace(" - ", "_")
    analytics_input = analytics_input.lower()

    # Check if the compliance selected is the level 1 or level 2 of the CIS
    is_level_1 = "level_1" in analytics_input
    analytics_input = analytics_input.replace("_level_1", "").replace("_level_2", "")

    # Filter the data based on the compliance selected
    if analytics_input == "All":
        analytics_input = None
        fig = px.pie(template="plotly")
        table = dcc.Graph(figure=fig, config={"displayModeBar": False})
        fig = px.pie()
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            showlegend=False,
            font=dict(size=17, color="#8a8d93"),
            hoverlabel=dict(font_size=14),
            paper_bgcolor="#303030",
        )
        pie_1 = dcc.Graph(
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "250px", "width": "250px", "right": "0px"},
        )
        pie_2 = dcc.Graph(
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "250px", "width": "250px", "right": "0px"},
        )

    else:

        # Use glob to find all CSV files in the folder
        csv_files = glob.glob(os.path.join(folder_path_compliance, "*.csv"))
        # Take only the files that match the compliance selected
        csv_files = [file for file in csv_files if analytics_input in file]

        def load_csv_files(csv_files):
            """Load CSV files into a single pandas DataFrame."""
            dfs = []
            for file in csv_files:
                df = pd.read_csv(file, sep=";", on_bad_lines="skip")
                dfs.append(df.astype(str))
            return pd.concat(dfs, ignore_index=True)
        
        data = load_csv_files(csv_files)

        if "gcp" in analytics_input:
            data = data.rename(columns={"LOCATION": "REGION"})

        # Filter the chosen level of the CIS
        if is_level_1:
            data = data[data["REQUIREMENTS_ATTRIBUTES_PROFILE"] == "Level 1"]

        if data.columns.str.contains("PROJECTID").any():
            data.rename(columns={"PROJECTID": "ACCOUNTID"}, inplace=True)

        # Filter ACCOUNT
        if account_filter == ["All"]:
            updated_cloud_account_values = data["ACCOUNTID"].unique()
        elif "All" in account_filter and len(account_filter) > 1:
            # Remove 'All' from the list
            account_filter.remove("All")
            updated_cloud_account_values = account_filter
        elif len(account_filter) == 0:
            updated_cloud_account_values = data["ACCOUNTID"].unique()
            account_filter = ["All"]
        else:
            updated_cloud_account_values = account_filter

        data = data[data["ACCOUNTID"].isin(updated_cloud_account_values)]

        account_filter_options = list(data["ACCOUNTID"].unique())
        account_filter_options = account_filter_options + ["All"]
        for item in account_filter_options:
            if item.__class__.__name__ != "str":
                if item is None or math.isnan(item):
                    account_filter_options.remove(item)

        # Filter REGION
        if region_filter_analytics == ["All"]:
            updated_region_account_values = data["REGION"].unique()
        elif "All" in region_filter_analytics and len(region_filter_analytics) > 1:
            # Remove 'All' from the list
            region_filter_analytics.remove("All")
            updated_region_account_values = region_filter_analytics
        elif len(region_filter_analytics) == 0:
            updated_region_account_values = data["REGION"].unique()
            region_filter_analytics = ["All"]
        else:
            updated_region_account_values = region_filter_analytics

        data = data[data["REGION"].isin(updated_region_account_values)]

        region_filter_options = list(data["REGION"].unique())
        region_filter_options = region_filter_options + ["All"]
        for item in region_filter_options:
            if item.__class__.__name__ != "str":
                region_filter_options.remove(item)

        data["ASSESSMENTDATE"] = pd.to_datetime(data["ASSESSMENTDATE"], errors="coerce")
        data["ASSESSMENTDATE"] = data["ASSESSMENTDATE"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Choosing the date that is the most recent
        data_values = data["ASSESSMENTDATE"].unique()
        data_values.sort()
        data_values = data_values[::-1]
        aux = []

        data_values = [str(i) for i in data_values]
        for value in data_values:
            if value.split(" ")[0] not in [
                aux[i].split(" ")[0] for i in range(len(aux))
            ]:
                aux.append(value)
        data_values = [str(i) for i in aux]

        data = data[data["ASSESSMENTDATE"].isin(data_values)]
        data["ASSESSMENTDATE"] = data["ASSESSMENTDATE"].apply(lambda x: x.split(" ")[0])

        options_date = data["ASSESSMENTDATE"].unique()
        options_date.sort()
        options_date = options_date[::-1]

        # Filter DATE
        if date_filter_analytics in options_date:
            data = data[data["ASSESSMENTDATE"] == date_filter_analytics]
        else:
            date_filter_analytics = options_date[0]
            data = data[data["ASSESSMENTDATE"] == date_filter_analytics]

        if data.empty:
            fig = px.pie()
            pie_1 = dcc.Graph(
                figure=fig,
                config={"displayModeBar": False},
                style={"height": "250px", "width": "250px", "right": "0px"},
            )

            return [
                html.Div(
                    [
                        html.H5(
                            "No data found for this compliance",
                            className="card-title",
                            style={"text-align": "left"},
                        )
                    ],
                    style={
                        "width": "99%",
                        "margin-right": "0.8%",
                        "margin-bottom": "10px",
                    },
                )
            ]
        else:
            # Check cases where the compliance start with AWS_
            if "aws_" in analytics_input:
                analytics_input = analytics_input + "_aws"
            try:
                current = analytics_input.replace(".", "_")
                compliance_module = importlib.import_module(f"dashboard.compliance.{current}")
                table = compliance_module.get_table(data)
            except ModuleNotFoundError as e:
                print(e)
                table = html.Div(
                    [
                        html.H5(
                            "No data found for this compliance",
                            className="card-title",
                            style={"text-align": "left", "color": "black"},
                        )
                    ],
                    style={
                        "width": "99%",
                        "margin-right": "0.8%",
                        "margin-bottom": "10px",
                    },
                )

            df = data.copy()
            df = df.groupby(["STATUS"]).size().reset_index(name="counts")
            df = df.sort_values(by=["counts"], ascending=False)
            df = df.reset_index(drop=True)

            # Pie 1

            pie_1 = get_pie(df)

            # Get the pie2 depending on the compliance
            df = data.copy()

            if (
                "REQUIREMENTS_ATTRIBUTES_SECTION" in df.columns
                and not df["REQUIREMENTS_ATTRIBUTES_SECTION"].isnull().values.any()
            ):
                pie_2 = get_polar_graph(df, "REQUIREMENTS_ATTRIBUTES_SECTION")
            elif (
                "REQUIREMENTS_ATTRIBUTES_CATEGORIA" in df.columns
                and not df["REQUIREMENTS_ATTRIBUTES_CATEGORIA"].isnull().values.any()
            ):
                pie_2 = get_polar_graph(df, "REQUIREMENTS_ATTRIBUTES_CATEGORIA")
            elif (
                "REQUIREMENTS_ATTRIBUTES_CATEGORY" in df.columns
                and not df["REQUIREMENTS_ATTRIBUTES_CATEGORY"].isnull().values.any()
            ):
                pie_2 = get_polar_graph(df, "REQUIREMENTS_ATTRIBUTES_CATEGORY")
            elif (
                "REQUIREMENTS_ATTRIBUTES_SERVICE" in df.columns
                and not df["REQUIREMENTS_ATTRIBUTES_SERVICE"].isnull().values.any()
            ):
                pie_2 = get_polar_graph(df, "REQUIREMENTS_ATTRIBUTES_SERVICE")
            else:
                fig = px.pie()
                fig.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    autosize=True,
                    showlegend=False,
                    paper_bgcolor="#303030",
                )
                pie_2 = dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": False},
                    style={"height": "250px", "width": "250px", "right": "0px"},
                )

    # Analytics table

    if not analytics_input:
        analytics_input = ""

    table_output = get_table(current_compliance, table)

    overall_status_result_graph = get_graph(pie_1, "Overall Status Result")

    security_level_graph = get_graph(pie_2, "Security Level")

    return (
        table_output,
        overall_status_result_graph,
        security_level_graph,
        account_filter,
        account_filter_options,
        region_filter_analytics,
        region_filter_options,
        date_filter_analytics,
        options_date,
    )

def get_graph(pie, title):
    return [
        html.Span(
            title,
            className="text-center text-prowler-stone-900 uppercase text-xs font-bold",
        ),
        html.Div(
            [pie],
            className="",
            style={
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "margin-top": "7%",
            },
        ),
    ]


def get_polar_graph(df, column_name):
    df = df[[column_name, "STATUS"]]
    df_pass = df[df["STATUS"] == "PASS"]
    df_pass = df_pass.groupby([column_name]).size().reset_index(name="counts")
    categories_pass = df_pass[column_name]
    # sort the categories
    categories_pass = sorted(categories_pass, key=lambda x: (isinstance(x, str), x))
    df_pass = df_pass.sort_values(by=["counts"], ascending=False)
    df_pass = df_pass.reset_index(drop=True)
    values_pass = df_pass.counts
    trace_pass = go.Scatterpolar(
        r=values_pass,
        theta=categories_pass,
        fill="toself",
        fillcolor="lightgreen",
        line=dict(color="green"),
        hovertemplate="Passed Findings: %{r}<extra></extra>",
        opacity=0.5,
        name="Passed Findings",
    )

    df_fail = df[df["STATUS"] == "FAIL"]
    df_fail = df_fail.groupby([column_name]).size().reset_index(name="counts")
    categories_fail = df_fail[column_name]
    # sort the categories
    categories_fail = sorted(categories_fail, key=lambda x: (isinstance(x, str), x))
    df_fail = df_fail.sort_values(by=["counts"], ascending=False)
    df_fail = df_fail.reset_index(drop=True)
    values_fail = df_fail.counts
    trace_fail = go.Scatterpolar(
        r=values_fail,
        theta=categories_fail,
        fill="toself",
        fillcolor="lightcoral",
        line=dict(color="red"),
        hovertemplate="Failed Findings: %{r}<extra></extra>",
        opacity=0.5,
        name="Failed Findings",
    )

    values = max(max(values_pass), max(values_fail))

    layout = go.Layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, np.max(values)],
            ),
            bgcolor="#5d5e5e",
        ),
        showlegend=True,
        paper_bgcolor="#FFF",
        plot_bgcolor="black",
        font=dict(color="#292524"),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    fig = {"data": [trace_pass, trace_fail], "layout": layout}

    pie = dcc.Graph(
        figure=fig,
        config={"displayModeBar": False},
        style={"height": "14.5rem", "width": "100%"},
    )

    return pie


def get_pie(df):
    # Define custom colors
    color_mapping = {
        "FAIL": "#FF7452",
        "PASS": "#36B37E",
        "INFO": "#2684FF",
        "WARN": "#260000",
        "MANUAL": "#8332A8",
    }

    # Use the color_discrete_map parameter to map categories to custom colors
    fig = px.pie(
        df,
        names="STATUS",
        values="counts",
        hole=0.7,
        color="STATUS",
        color_discrete_map=color_mapping,
    )
    fig.update_traces(
        hovertemplate=None,
        textposition="outside",
        textinfo="percent+label",
        rotation=50,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        showlegend=False,
        font=dict(size=14, color="#292524"),
        hoverlabel=dict(font_size=12),
        paper_bgcolor="#FFF",
    )

    pie = dcc.Graph(
        figure=fig,
        config={"displayModeBar": False},
        style={"height": "20rem", "width": "20rem"},
    )

    return pie

def get_table(current_compliance, table):
    return [
        html.Div(
            [
                html.H5(
                    f"{current_compliance}",
                    className="text-prowler-stone-900 text-md font-bold uppercase mb-4",
                ),
                table,
            ],
            className="relative flex flex-col bg-white shadow-provider rounded-xl px-4 py-3 flex-wrap w-full",
        ),
    ]