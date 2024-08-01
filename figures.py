import plotly.graph_objs as go
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


# Dictionary to map db_year to full names
db_year_fullname = {
    'ebird19': 'eBird 2019',
    'ebird22': 'eBird 2022',
    'inat19': 'iNat 2019',
    'inat22': 'iNat 2022'
}

# Dictionary to map db_year to line color
db_year_color_dict = {
    'ebird19': '#e98b81',  # red
    'ebird22': '#a4c062',  # green
    'inat19': '#56bcc2',  # blue
    'inat22': '#c188f8',  # purple
}

# Function to convert day of year to date string
def day_of_year_to_date_str(day_of_year):
    """Converts numeric day to string in the form of 'Month Day'"""
    day_of_year = int(day_of_year)
    date = datetime(2023, 1, 1) + timedelta(days=day_of_year-1)
    return date.strftime('%b %d')


# Rectangular plot function
def rectangular_plot(bird_dict, birds_df, bird_ids, scale_type, max_y_value):
    fig_rect = go.Figure()
    for bird_id in bird_ids:
        common_name = bird_dict[bird_id]
        df_filtered = birds_df[birds_df['AVIBASEID'] == bird_id].copy()  # Filter for specific bird
        week_1_data = df_filtered[df_filtered['week'] == 1].copy()  # Duplicate week 1 and add to end as week 53
        week_1_data['week'] = 53
        df_filtered = pd.concat([df_filtered, week_1_data], ignore_index=True)
        df_filtered['day'] = df_filtered['week'].apply(lambda w: (w - 1) * 7 + 1)  # Convert weeks to days

        seasonal_properties = [
            (0, 79, 'rgba(179, 131, 255, 0.25)', 'Winter'),
            (79, 171, 'rgba(0, 186, 56, 0.25)', 'Spring'),
            (171, 264, 'rgba(163, 165, 0, 0.25)', 'Summer'),
            (264, 355, 'rgba(229, 135, 0, 0.25)', 'Fall'),
            (355, 365, 'rgba(179, 131, 255, 0.25)', 'Winter')
        ]

        # Add colored rectangles for each season
        winter_added = False
        for xmin, xmax, color, season in seasonal_properties:
            show_legend = True
            legend_group = season
            if season == 'Winter':
                if winter_added:
                    show_legend = False
                else:
                    winter_added = True

            fig_rect.add_trace(go.Scatter(
                x=[xmin, xmax, xmax, xmin, xmin],
                y=[0, 0, 1, 1, 0],
                fill='toself',
                fillcolor=color,
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='none',
                showlegend=show_legend,
                legendgroup=legend_group,  # Linking both Winter regions
                name=season
            ))

        # Create an interpolated trace for each db_year
        all_days = np.arange(1, 366)
        db_years_added = set()
        for db_year in df_filtered['yr_db'].unique():
            # Generate interpolated values for all days in the year
            df_db_year = df_filtered[df_filtered['yr_db'] == db_year]
            interp_func = interp1d(df_db_year['day'], df_db_year['count'], kind='quadratic', fill_value="extrapolate")
            interpolated_values = interp_func(all_days)
            
            # Determine if this db_year should be shown in the legend (prevents duplicates)
            show_legend = db_year not in db_years_added
            if show_legend:
                db_years_added.add(db_year)
            
            # Add trace to the figure
            fig_rect.add_trace(go.Scatter(
                x=all_days, 
                y=interpolated_values,
                mode='lines',
                name=db_year_fullname.get(db_year, db_year),
                line=dict(width=3.5, color=db_year_color_dict.get(str(db_year), '#000000')),
                showlegend=show_legend,
                hovertemplate='<b>%{text}</b>: %{y:.4f}<extra></extra>',
                text=[day_of_year_to_date_str(day) for day in all_days]
            ))

    # Add grey dashed line
    fig_rect.add_shape(type="line",
                       x0=1, x1=52 * 7, y0=1 / 52, y1=1 / 52,
                       line=dict(color="grey", dash='dash', width=3))

    # Determine scale of y-axis based on user input
    if scale_type == 'fixed':
        yaxis_range = [0, 0.12]
    else:
        yaxis_range = [0, max_y_value]

    # Create x-axis tick values and labels for Jan 1 and Seasons
    tickvals = [1, 79, 171, 264, 355]
    ticktext = [day_of_year_to_date_str(day) for day in tickvals]

    # Update plot with new x and y axis, remove zoom option, add legend
    fig_rect.update_layout(
        xaxis=dict(title='Date', title_font=dict(size=18), range=[1, 366], tickvals=tickvals, ticktext=ticktext),
        yaxis=dict(title='Relative Frequency of Bird Sighting', title_font=dict(size=18), range=yaxis_range),
        title=dict(text=f'{common_name}', x=0.5, xanchor='center'),
        dragmode='pan',
        modebar=dict(remove=['zoom', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale']),
        legend=dict(
                title=dict(text='Database/Year and Season', font=dict(size=12)))
    )

    return fig_rect


# Circular plot function
def circular_plot(bird_dict, birds_df, bird_ids, scale_type, max_y_value):
    for bird_id in bird_ids:
        common_name = bird_dict[bird_id]
        df_filtered = birds_df[birds_df['AVIBASEID'] == bird_id].copy()  # Filter for specific bird
        week_1_data = df_filtered[df_filtered['week'] == 1].copy()  # Duplicate week 1 and add to end as week 53
        week_1_data['week'] = 53
        df_filtered = pd.concat([df_filtered, week_1_data], ignore_index=True)
        df_filtered['day'] = df_filtered['week'].apply(lambda w: (w - 1) * 7 + 1)  # Convert weeks to days

        # Define color coding schemes for the seasons
        seasonal_properties = [
            (0, 79, 'rgba(179, 131, 255, 0.25)', 'Winter'),
            (79, 171, 'rgba(0, 186, 56, 0.25)', 'Spring'),
            (171, 264, 'rgba(163, 165, 0, 0.25)', 'Summer'),
            (264, 355, 'rgba(229, 135, 0, 0.25)', 'Fall'),
            (355, 365, 'rgba(179, 131, 255, 0.25)', 'Winter')
        ]

        # Polar plot
        df_filtered['week_rad'] = df_filtered['week'] * 2 * np.pi / 52
        fig_polar = go.Figure()

        # Add colored arcs for seasons
        winter_added = False
        for start_week, end_week, color, season in seasonal_properties:
            show_legend = True
            legend_group = season
            if season == 'Winter':
                if winter_added:
                    show_legend = False
                else:
                    winter_added = True
            start_deg = start_week * 360 / 364
            end_deg = end_week * 360 / 364
            theta = np.linspace(start_deg, end_deg, 100)
            r = np.ones_like(theta)

            fig_polar.add_trace(go.Scatterpolar(
                r=np.concatenate([[0], r, [0]]),
                theta=np.concatenate([[start_deg], theta, [end_deg]]),
                fill='toself',
                fillcolor=color,
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='none',
                showlegend=show_legend,
                legendgroup=legend_group,  # Linking both Winter regions
                name=season
            ))

        # Create an interpolated trace for each db_year
        all_days = np.arange(1, 366)
        for db_year in df_filtered['yr_db'].unique():
            # Create interpolation counts
            df_db_year = df_filtered[df_filtered['yr_db'] == db_year]
            interp_func = interp1d(df_db_year['day'], df_db_year['count'], kind='quadratic', fill_value="extrapolate")
            interpolated_counts = interp_func(all_days)
            interpolated_theta = all_days * 360 / 365 
            
            # Add trace to the polar figure
            fig_polar.add_trace(go.Scatterpolar(
                r=interpolated_counts,
                theta=interpolated_theta,
                mode='lines',
                name=db_year_fullname.get(db_year, db_year),
                line=dict(width=3.5, color=db_year_color_dict.get(str(db_year), '#000000')),
                hovertemplate='<b>%{text}</b>: %{r:.4f}<extra></extra>',
                text=[day_of_year_to_date_str(day) for day in all_days]
            ))

        # Add Gray Dashed Line
        fig_polar.add_trace(go.Scatterpolar(
            r=[1 / 52] * 100, theta=np.linspace(0, 360, 100),
            mode='lines', line=dict(color='grey', dash='dash', width=3),
            showlegend=False, hoverinfo='none'
        ))

    # Determine radial axis range based on user input
    radial_range = [0, 0.12] if scale_type == 'fixed' else [0, max_y_value]

    # Ticks for Seasons and Jan 1
    tickvals = [1, 79, 171, 264, 355]
    ticktext = [day_of_year_to_date_str(day) for day in tickvals]

    # Edit Layout of Circular Graph (axis, title, and legend)
    fig_polar.update_layout(
        # Add x-axis ticks and labels
        polar=dict(
            radialaxis=dict(visible=True, range=radial_range, angle=90),
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
                tickmode='array',
                tickvals=[0, 79/365*360, 171/365*360, 264/365*360, 355/365*360],
                ticktext=ticktext
            )
        ),
        # Add title
        title=dict(text=f'{common_name}', x=0.5, xanchor='center'),
        # Add x-axis label
        annotations=[
            dict(
                x=0.5,
                y=-0.2,
                xref='paper',
                yref='paper',
                showarrow=False,
                text='Date',  
                font=dict(size=16)
            )],
        # Add legend
        legend=dict(
            title=dict(text='Database/Year and Season', font=dict(size=13)),
            x=1.3,
            y=0.5,
            xanchor='left',
            yanchor='middle'))
    return fig_polar


# Side-by-side plot functions
def create_sidebysideplot(bird_dict, birds_df, bird_id, scale_type='fixed'):
    common_name = bird_dict[bird_id]
    df_filtered = birds_df[birds_df['AVIBASEID'] == bird_id].copy()  # Filter for specific bird
    week_1_data = df_filtered[df_filtered['week'] == 1].copy()  # Duplicate week 1 and add to end as week 53
    week_1_data['week'] = 53
    df_filtered = pd.concat([df_filtered, week_1_data], ignore_index=True)
    df_filtered['day'] = df_filtered['week'].apply(lambda w: (w - 1) * 7 + 1)  # Convert weeks to days

    # Define color coding schemes for the seasons
    seasonal_dimensions = [
        (0, 79, 'rgba(179, 131, 255, 0.25)', 'Winter'),
        (79, 171, 'rgba(0, 186, 56, 0.25)', 'Spring'),
        (171, 264, 'rgba(163, 165, 0, 0.25)', 'Summer'),
        (264, 355, 'rgba(229, 135, 0, 0.25)', 'Fall'),
        (355, 365, 'rgba(179, 131, 255, 0.25)', 'Winter')
    ]

    # Create subplots: 1 row, 2 columns
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Rectangular Plot', 'Polar Plot'), specs=[[{"type": "xy"}, {"type": "polar"}]])

    # Add colored spans for seasons in both plots
    added_seasons = set()
    for xmin, xmax, color, season in seasonal_dimensions:
        show_legend = season not in added_seasons
        added_seasons.add(season)
        fig.add_trace(go.Scatter(
            x=[xmin, xmax, xmax, xmin, xmin],
            y=[0, 0, 1, 1, 0],  # closing the polygon
            fill='toself',
            fillcolor=color,
            line=dict(color='rgba(0,0,0,0)'),
            hoverinfo='none',
            showlegend=show_legend,
            legendgroup=season,
            name=season
        ), row=1, col=1)
        fig.add_trace(go.Scatterpolar(
            r=[0, 1, 1, 0],
            theta=[xmin * 360 / 365, xmin * 360 / 365, xmax * 360 / 365, xmax * 360 / 365],
            fill='toself',
            fillcolor=color,
            line=dict(color='rgba(0,0,0,0)'),
            hoverinfo='none',
            showlegend=False,
            legendgroup=season,
            name=season
        ), row=1, col=2)

    # Create an interpolated trace for each db_year in the rectangular plot
    all_days = np.arange(0, 366)
    db_years_added = set()
    for db_year in df_filtered['yr_db'].unique():
        df_db_year = df_filtered[df_filtered['yr_db'] == db_year]
        interp_func = interp1d(df_db_year['day'], df_db_year['count'], kind='quadratic', fill_value="extrapolate")
        interpolated_counts = interp_func(all_days)
        
        show_legend = db_year not in db_years_added
        db_years_added.add(db_year)
        
        fig.add_trace(go.Scatter(
            x=all_days, 
            y=interpolated_counts, 
            mode='lines', 
            name=db_year_fullname.get(db_year, db_year),
            line=dict(width = 3.5, color=db_year_color_dict.get(str(db_year), '#000000')),
            showlegend=show_legend,
            legendgroup=str(db_year),
            hovertemplate='<b>%{text}</b>: %{y:.4f}<extra></extra>',
            text=[day_of_year_to_date_str(day) for day in all_days]
        ), row=1, col=1)

    # Create an interpolated trace for each db_year in the polar plot
    all_days = np.arange(1, 366)
    db_years_added = set()
    for db_year in df_filtered['yr_db'].unique():
        df_db_year = df_filtered[df_filtered['yr_db'] == db_year]
        interp_func = interp1d(df_db_year['day'], df_db_year['count'], kind='linear', fill_value="extrapolate")
        interpolated_counts = interp_func(all_days)
        interpolated_theta = all_days * 360 / 365 
        
        show_legend = db_year not in db_years_added
        db_years_added.add(db_year)
        
        fig.add_trace(go.Scatterpolar(
            r=interpolated_counts,
            theta=interpolated_theta,
            mode='lines',
            name=db_year_fullname.get(db_year, db_year),
            line=dict(width=3.5, color=db_year_color_dict.get(str(db_year), '#000000')),
            hovertemplate='<b>%{text}</b>: %{r:.4f}<extra></extra>',
            text=[day_of_year_to_date_str(day) for day in all_days],
            showlegend=False,
            legendgroup=str(db_year)
        ), row=1, col=2)

    # Add Gray Dashed Line in the rectangular plot
    fig.add_shape(type="line",
                  x0=1, x1=53 * 7, y0=1 / 52, y1=1 / 52,
                  line=dict(color="grey", dash='dash', width=3), row=1, col=1)

    # Add Gray Dashed Line in the polar plot
    fig.add_trace(go.Scatterpolar(
        r=[1 / 52] * 100, theta=np.linspace(0, 360, 100),
        mode='lines', line=dict(color='grey', dash='dash', width=3),
        showlegend=False, hoverinfo='none'
    ), row=1, col=2)

    # Determine y-axis range based on user selection
    if scale_type == 'fixed':
        yaxis_range = [0, 0.12]
    else:
        yaxis_range = [0, df_filtered['count'].max() * 1.1]

    # Create x-axis tick values and labels for Jan 1 and Seasons
    tickvals = [1, 79, 171, 264, 355]
    ticktext = [day_of_year_to_date_str(day) for day in tickvals]

    # Update rectangular plot layout
    fig.update_xaxes(title_text='Date', title_font_size=14, range=[1, 366], 
                    tickvals=tickvals, ticktext=ticktext, tickfont_size=14, row=1, col=1)
    fig.update_yaxes(title_text='Relative Frequency of Bird Sighting', title_font_size=14,
                    tickfont_size=14, range=yaxis_range, row=1, col=1)

    # Update polar plot layout
    radial_range = [0, 0.12] if scale_type == 'fixed' else [0, df_filtered['count'].max() * 1.1]
    fig.update_layout(
        title=dict(
            text=f"<b>{common_name} Seasonality Pattern</b>",
            font=dict(size=22),
            x=0.5,
            xanchor='center'
        ),
        polar=dict(
            radialaxis=dict(visible=True, range=radial_range, angle=90),
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
                tickmode='array',
                tickvals=[0, 79/365*360, 171/365*360, 264/365*360, 355/365*360],
                #font=dict(size=16),
                ticktext=ticktext
            )
        ),
        annotations=[
            dict(
                x=0.78,
                y=-0.15,
                xref='paper',
                yref='paper',
                showarrow=False,
                font=dict(size=16),
                text='Date'
            )],
        legend=dict(
            title=dict(text='Database/Year and Season', font=dict(size=12)),
            x=0.61,  # Adjust position to place legend between the plots
            y=1.0,
            xanchor='right',
            yanchor='top'
        ),
        modebar=dict(
            remove=['zoom', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale']
        )
    )
    fig.update_layout(
        margin={'t':80,'l':0,'b':60,'r':0}
    )

    return fig
