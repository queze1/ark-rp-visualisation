from dash import Input, Output, State, ctx

from core import PlotBuilder
from core.enums import PlotType, Tab
from core.models import AxisConfig, FigureConfig, FilterConfig
from utils.logging_setup import get_logger
from utils.serialisation import encode_state

from .patterns import (
    match_agg_dropdowns,
    match_axes,
    match_fields,
    match_filter_operators,
    match_filter_types,
    match_filter_value_inputs,
    match_fullscreen_button,
    match_fullscreen_button_icon,
    match_graph,
    match_mavg_7,
    match_mavg_30,
    match_sort_axis,
    match_sort_order,
    match_title_input,
    match_update_graph,
    match_x_label,
    match_x_log,
    match_y_label,
    match_y_log,
)

logger = get_logger(__name__)


def register_graph_callbacks(app):
    def render_graph(
        n_clicks,
        selected_fields,
        selected_axes,
        selected_aggregations,
        filters,
        customisation,
    ):
        if n_clicks is None or not all(selected_fields) or not ctx.triggered_id:
            return dict(
                fig={},
                fullscreen_url="#",
                fullscreen_disabled=True,
            )

        active_tab = Tab(ctx.triggered_id["tab"])

        # Log graph creation
        summary = f"""
        User created a graph:
            Tab: {active_tab.label}
            {selected_axes[0]}: {selected_fields[0]}
            {selected_axes[1]}: {selected_fields[1]}
            Aggregations: {selected_aggregations}
            Filters: {filters}
            Customizations: {customisation}
        """
        logger.info(summary.strip())

        # 1. Create a fullscreen URL which renders this graph
        graph_state = {
            "tab": active_tab.value,
            "fields": selected_fields,
            "axes": selected_axes,
            "aggs": selected_aggregations,
            "filters": filters,
            "custom": customisation,
        }
        encoded_params = encode_state(graph_state)
        fullscreen_url = f"/graph?state={encoded_params}"

        # 2. Build the figure
        fig = PlotBuilder(
            plot_type=PlotType(active_tab.plot_type),
            axis_config=AxisConfig.from_raw(
                selected_fields=selected_fields,
                selected_axes=selected_axes,
                selected_aggregations=selected_aggregations,
            ),
            filter_config=FilterConfig.from_raw(*filters),
            figure_config=FigureConfig.from_raw(**customisation),
        ).build()

        return dict(
            fig=fig,
            fullscreen_url=fullscreen_url,
            fullscreen_disabled=False,
        )

    app.callback(
        output=dict(
            fig=Output(match_graph, "figure"),
            fullscreen_url=Output(match_fullscreen_button, "href"),
            fullscreen_disabled=Output(match_fullscreen_button_icon, "disabled"),
        ),
        inputs=dict(
            n_clicks=Input(match_update_graph, "n_clicks"),
            selected_fields=State(match_fields, "value"),
            selected_axes=State(match_axes, "children"),
            selected_aggregations=State(
                match_agg_dropdowns,
                "value",
            ),
            filters=(
                State(
                    match_filter_types,
                    "value",
                ),
                State(
                    match_filter_operators,
                    "value",
                ),
                State(
                    match_filter_value_inputs,
                    "value",
                ),
            ),
            customisation=dict(
                title=State(match_title_input, "value"),
                x_label=State(match_x_label, "value"),
                y_label=State(match_y_label, "value"),
                moving_averages={
                    7: State(match_mavg_7, "checked"),
                    30: State(match_mavg_30, "checked"),
                },
                sort_order=State(match_sort_order, "value"),
                sort_axis=State(match_sort_axis, "value"),
                x_log=State(match_x_log, "checked"),
                y_log=State(match_y_log, "checked"),
            ),
        ),
    )(render_graph)
