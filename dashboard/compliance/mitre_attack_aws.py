import warnings

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dash_table, dcc, html

warnings.filterwarnings("ignore")
import dash_table
from dashboard.common_methods import map_status_to_icon
from dashboard.config import pass_emoji, fail_emoji

def get_table(data):
    aux = data[
        [
            "REQUIREMENTS_ID",
            "REQUIREMENTS_SUBTECHNIQUES",
            "CHECKID",
            "STATUS",
            "REGION",
            "ACCOUNTID",
            "RESOURCEID",
        ]
    ].copy()
    aux["STATUS"] = aux["STATUS"].apply(map_status_to_icon)
    aux["REQUIREMENTS_ID"] = aux["REQUIREMENTS_ID"].astype(str)
    aux.drop_duplicates(keep="first", inplace=True)
    findings_counts_subtechniques = (
        aux.groupby(["REQUIREMENTS_SUBTECHNIQUES", "STATUS"])
        .size()
        .unstack(fill_value=0)
    )
    findings_counts_id = (
        aux.groupby(["REQUIREMENTS_ID", "STATUS"]).size().unstack(fill_value=0)
    )

    section_containers = []

    for req_id in aux["REQUIREMENTS_ID"].unique():
        success_req_id = (
            findings_counts_id.loc[req_id, pass_emoji]
            if pass_emoji in findings_counts_id.columns
            else 0
        )
        failed_req_id = (
            findings_counts_id.loc[req_id, fail_emoji]
            if fail_emoji in findings_counts_id.columns
            else 0
        )

        fig_req_id = go.Figure(
            data=[
                go.Bar(
                    name="Failed",
                    x=[failed_req_id],
                    y=[""],
                    orientation="h",
                    marker=dict(color="#A3231F"),
                    width=[0.8],
                ),
                go.Bar(
                    name="Success",
                    x=[success_req_id],
                    y=[""],
                    orientation="h",
                    marker=dict(color="#1FB53F"),
                    width=[0.8],
                ),
            ]
        )

        fig_req_id.update_layout(
            barmode="stack",
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            width=350,
            height=30,
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            annotations=[
                dict(
                    x=success_req_id + failed_req_id,
                    y=0,
                    xref="x",
                    yref="y",
                    text=str(success_req_id),
                    showarrow=False,
                    font=dict(color="#1FB53F", size=14),
                    xanchor="left",
                    yanchor="middle",
                ),
                dict(
                    x=0,
                    y=0,
                    xref="x",
                    yref="y",
                    text=str(failed_req_id),
                    showarrow=False,
                    font=dict(color="#A3231F", size=14),
                    xanchor="right",
                    yanchor="middle",
                ),
            ],
        )

        fig_req_id.add_annotation(
            x=50,
            y=0,
            text="",
            showarrow=False,
            align="center",
            xanchor="center",
            yanchor="middle",
            textangle=0,
        )

        fig_req_id.add_annotation(
            x=failed_req_id,
            y=0.3,
            text="|",
            showarrow=False,
            align="center",
            xanchor="center",
            yanchor="middle",
            textangle=0,
            font=dict(size=20),
        )

        graph_req_id = dcc.Graph(
            figure=fig_req_id, config={"staticPlot": True}, className="info-bar"
        )

        graph_div = html.Div(graph_req_id, className="graph-req_id")

        direct_internal_items = []
        for subtechnique in aux[aux["REQUIREMENTS_ID"] == req_id][
            "REQUIREMENTS_SUBTECHNIQUES"
        ].unique():
            specific_data = aux[
                (aux["REQUIREMENTS_ID"] == req_id)
                & (aux["REQUIREMENTS_SUBTECHNIQUES"] == subtechnique)
            ]
            success_subtechinque = (
                findings_counts_subtechniques.loc[subtechnique, pass_emoji]
                if pass_emoji in findings_counts_subtechniques.columns
                else 0
            )
            failed_subtechinque = (
                findings_counts_subtechniques.loc[subtechnique, fail_emoji]
                if fail_emoji in findings_counts_subtechniques.columns
                else 0
            )

            # Create the DataTable for subtechnique
            data_table = dash_table.DataTable(
                data=specific_data.to_dict("records"),
                columns=[
                    {"name": i, "id": i}
                    for i in ["CHECKID", "STATUS", "REGION", "ACCOUNTID", "RESOURCEID"]
                ],
                style_table={"overflowX": "auto"},
                style_as_list_view=True,
                style_cell={"textAlign": "left", "padding": "5px"},
            )

            # Create the graph for subtechnique
            fig_subtechinque = go.Figure(
                data=[
                    go.Bar(
                        name="Failed",
                        x=[failed_subtechinque],
                        y=[""],
                        orientation="h",
                        marker=dict(color="#A3231F"),
                    ),
                    go.Bar(
                        name="Success",
                        x=[success_subtechinque],
                        y=[""],
                        orientation="h",
                        marker=dict(color="#1FB53F"),
                    ),
                ]
            )

            fig_subtechinque.update_layout(
                barmode="stack",
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                width=350,
                height=30,
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                annotations=[
                    dict(
                        x=success_subtechinque + failed_subtechinque,
                        y=0,
                        xref="x",
                        yref="y",
                        text=str(success_subtechinque),
                        showarrow=False,
                        font=dict(color="#1FB53F", size=14),
                        xanchor="left",
                        yanchor="middle",
                    ),
                    dict(
                        x=0,
                        y=0,
                        xref="x",
                        yref="y",
                        text=str(failed_subtechinque),
                        showarrow=False,
                        font=dict(color="#A3231F", size=14),
                        xanchor="right",
                        yanchor="middle",
                    ),
                ],
            )

            fig_subtechinque.add_annotation(
                x=50,
                y=0,
                text="",
                showarrow=False,
                align="center",
                xanchor="center",
                yanchor="middle",
                textangle=0,
            )

            fig_subtechinque.add_annotation(
                x=failed_subtechinque,
                y=0.3,
                text="|",
                showarrow=False,
                align="center",
                xanchor="center",
                yanchor="middle",
                textangle=0,
                font=dict(size=20),
            )

            graph_subtechinque = dcc.Graph(
                figure=fig_subtechinque,
                config={"staticPlot": True},
                className="info-bar-child",
            )

            graph_div_subtechinque = html.Div(
                graph_subtechinque, className="graph-section-subtechinque"
            )

            internal_accordion_item = dbc.AccordionItem(
                title=subtechnique,
                children=[html.Div([data_table], className="inner-accordion-content")],
            )

            internal_section_container = html.Div(
                [
                    graph_div_subtechinque,
                    dbc.Accordion(
                        [internal_accordion_item], start_collapsed=True, flush=True
                    ),
                ],
                className="accordion-inner--child",
            )

            direct_internal_items.append(internal_section_container)

        accordion_item = dbc.AccordionItem(
            title=f"{req_id}", children=direct_internal_items
        )
        section_container = html.Div(
            [
                graph_div,
                dbc.Accordion([accordion_item], start_collapsed=True, flush=True),
            ],
            className="accordion-inner",
        )

        section_containers.append(section_container)

    return html.Div(section_containers, className="compliance-data-layout")