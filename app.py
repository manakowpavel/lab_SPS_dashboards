import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from base64 import b64decode
import io

# Инициализация приложения
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Дашборд: Процесс разработки ПО"

# Глобальная переменная для хранения данных
df_global = None

# Layout приложения
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 Дашборд: Процесс разработки программного обеспечения", 
                   className="text-center text-primary mb-4"),
            html.P("Интерактивный инструмент для анализа метрик разработки ПО", 
                  className="text-center text-muted mb-4")
        ])
    ]),

    # Загрузка файла
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📁 Загрузка данных", className="card-title"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Перетащите CSV файл или ',
                            html.A('выберите файл')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id='output-data-upload', className="mt-2")
                ])
            ], className="mb-4")
        ])
    ]),

    # Фильтры
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Выберите период анализа:", className="fw-bold"),
                    dcc.Dropdown(
                        id='period-dropdown',
                        options=[
                            {'label': 'Все периоды', 'value': 'all'},
                            {'label': 'Квартал 1', 'value': 'Q1'},
                            {'label': 'Квартал 2', 'value': 'Q2'},
                            {'label': 'Квартал 3', 'value': 'Q3'},
                            {'label': 'Квартал 4', 'value': 'Q4'}
                        ],
                        value='all',
                        clearable=False
                    )
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Фильтр по фазе:", className="fw-bold"),
                    dcc.Dropdown(
                        id='phase-dropdown',
                        options=[],
                        value=None,
                        multi=True,
                        placeholder="Выберите фазы..."
                    )
                ])
            ])
        ], width=6)
    ], className="mb-4"),

    # Индикаторы KPI
    html.Div(id='kpi-indicators', className="mb-4"),

    # Графики - Ряд 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📈 График 1: Динамика завершенных задач", className="card-title"),
                    dcc.Graph(id='time-series-tasks')
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🥧 График 2: Распределение по фазам разработки", className="card-title"),
                    dcc.Graph(id='pie-chart-phases')
                ])
            ])
        ], width=6)
    ], className="mb-4"),

    # Графики - Ряд 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 График 3: Сравнение часов по активностям", className="card-title"),
                    dcc.Graph(id='bar-chart-hours')
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🔍 График 4: Корреляция Velocity и качества кода", className="card-title"),
                    dcc.Graph(id='scatter-correlation')
                ])
            ])
        ], width=6)
    ], className="mb-4"),

    # Таблица данных
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📋 График 5: Таблица ключевых метрик", className="card-title"),
                    html.Div(id='data-table')
                ])
            ])
        ])
    ])

], fluid=True, style={'padding': '20px'})


# Callback для загрузки данных
@app.callback(
    [Output('output-data-upload', 'children'),
     Output('phase-dropdown', 'options')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    global df_global

    if contents is None:
        return html.Div("Загрузите CSV файл для начала работы", className="text-danger"), []

    try:
        content_type, content_string = contents.split(',')
        decoded = b64decode(content_string)
        df_global = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Получение уникальных фаз для dropdown
        if 'Категория_фазы' in df_global.columns:
            phases = [{'label': phase, 'value': phase} 
                     for phase in df_global['Категория_фазы'].unique()]
        else:
            phases = []

        return html.Div([
            html.I(className="bi bi-check-circle-fill text-success me-2"),
            f"✅ Файл '{filename}' успешно загружен! Записей: {len(df_global)}"
        ], className="text-success"), phases

    except Exception as e:
        return html.Div(f"❌ Ошибка при загрузке файла: {str(e)}", className="text-danger"), []


# Callback для KPI индикаторов
@app.callback(
    Output('kpi-indicators', 'children'),
    [Input('period-dropdown', 'value'),
     Input('phase-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_kpi(period, phases, upload_contents):
    if df_global is None:
        return html.Div("Загрузите данные для отображения KPI", className="alert alert-info")

    df_filtered = filter_data(df_global, period, phases)

    if df_filtered.empty:
        return html.Div("Нет данных для выбранных фильтров", className="alert alert-warning")

    # Вычисление KPI
    total_tasks = df_filtered['Завершенные_задачи'].sum() if 'Завершенные_задачи' in df_filtered.columns else 0
    avg_velocity = df_filtered['Velocity_SP'].mean() if 'Velocity_SP' in df_filtered.columns else 0
    avg_quality = df_filtered['Качество_кода_%'].mean() if 'Качество_кода_%' in df_filtered.columns else 0
    total_bugs_fixed = df_filtered['Баги_исправлено'].sum() if 'Баги_исправлено' in df_filtered.columns else 0

    kpi_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Всего задач завершено", className="text-muted"),
                    html.H3(f"{int(total_tasks)}", className="text-primary")
                ])
            ], className="text-center")
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Средний Velocity (SP)", className="text-muted"),
                    html.H3(f"{avg_velocity:.1f}", className="text-success")
                ])
            ], className="text-center")
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Среднее качество кода (%)", className="text-muted"),
                    html.H3(f"{avg_quality:.1f}%", className="text-info")
                ])
            ], className="text-center")
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Багов исправлено", className="text-muted"),
                    html.H3(f"{int(total_bugs_fixed)}", className="text-warning")
                ])
            ], className="text-center")
        ], width=3)
    ])

    return kpi_cards


# Функция фильтрации данных
def filter_data(df, period, phases):
    if df is None:
        return pd.DataFrame()

    df_filtered = df.copy()

    # Фильтр по периоду
    if period != 'all' and 'Дата' in df.columns:
        df_filtered['Дата'] = pd.to_datetime(df_filtered['Дата'])
        df_filtered['Quarter'] = df_filtered['Дата'].dt.quarter
        quarter_map = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
        if period in quarter_map:
            df_filtered = df_filtered[df_filtered['Quarter'] == quarter_map[period]]

    # Фильтр по фазам
    if phases and 'Категория_фазы' in df.columns:
        df_filtered = df_filtered[df_filtered['Категория_фазы'].isin(phases)]

    return df_filtered


# График 1: Временной ряд
@app.callback(
    Output('time-series-tasks', 'figure'),
    [Input('period-dropdown', 'value'),
     Input('phase-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_time_series(period, phases, upload_contents):
    if df_global is None:
        return go.Figure().add_annotation(text="Загрузите данные", showarrow=False)

    df_filtered = filter_data(df_global, period, phases)

    if df_filtered.empty or 'Месяц' not in df_filtered.columns:
        return go.Figure().add_annotation(text="Нет данных", showarrow=False)

    fig = go.Figure()

    if 'Завершенные_задачи' in df_filtered.columns:
        fig.add_trace(go.Scatter(
            x=df_filtered['Месяц'],
            y=df_filtered['Завершенные_задачи'],
            mode='lines+markers',
            name='Завершенные задачи',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        ))

    if 'Активные_задачи' in df_filtered.columns:
        fig.add_trace(go.Scatter(
            x=df_filtered['Месяц'],
            y=df_filtered['Активные_задачи'],
            mode='lines+markers',
            name='Активные задачи',
            line=dict(color='#A23B72', width=3, dash='dash'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        xaxis_title="Период",
        yaxis_title="Количество задач",
        hovermode='x unified',
        template='plotly_white'
    )

    return fig


# График 2: Круговая диаграмма
@app.callback(
    Output('pie-chart-phases', 'figure'),
    [Input('period-dropdown', 'value'),
     Input('phase-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_pie_chart(period, phases, upload_contents):
    if df_global is None:
        return go.Figure().add_annotation(text="Загрузите данные", showarrow=False)

    df_filtered = filter_data(df_global, period, phases)

    if df_filtered.empty or 'Категория_фазы' not in df_filtered.columns:
        return go.Figure().add_annotation(text="Нет данных", showarrow=False)

    phase_counts = df_filtered['Категория_фазы'].value_counts()

    fig = px.pie(
        values=phase_counts.values,
        names=phase_counts.index,
        title="",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


# График 3: Гистограмма
@app.callback(
    Output('bar-chart-hours', 'figure'),
    [Input('period-dropdown', 'value'),
     Input('phase-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_bar_chart(period, phases, upload_contents):
    if df_global is None:
        return go.Figure().add_annotation(text="Загрузите данные", showarrow=False)

    df_filtered = filter_data(df_global, period, phases)

    if df_filtered.empty:
        return go.Figure().add_annotation(text="Нет данных", showarrow=False)

    fig = go.Figure()

    hours_columns = ['Code_Review_часов', 'Тестирование_часов', 'Разработка_часов']
    colors = ['#F18F01', '#C73E1D', '#6A994E']

    for col, color in zip(hours_columns, colors):
        if col in df_filtered.columns:
            fig.add_trace(go.Bar(
                x=df_filtered['Месяц'] if 'Месяц' in df_filtered.columns else df_filtered.index,
                y=df_filtered[col],
                name=col.replace('_', ' '),
                marker_color=color
            ))

    fig.update_layout(
        barmode='group',
        xaxis_title="Период",
        yaxis_title="Часы",
        template='plotly_white'
    )

    return fig


# График 4: График рассеяния
@app.callback(
    Output('scatter-correlation', 'figure'),
    [Input('period-dropdown', 'value'),
     Input('phase-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_scatter(period, phases, upload_contents):
    if df_global is None:
        return go.Figure().add_annotation(text="Загрузите данные", showarrow=False)

    df_filtered = filter_data(df_global, period, phases)

    if df_filtered.empty or 'Velocity_SP' not in df_filtered.columns or 'Качество_кода_%' not in df_filtered.columns:
        return go.Figure().add_annotation(text="Нет данных", showarrow=False)

    # Берём только нужные столбцы и убираем NaN
    df_plot = df_filtered[['Velocity_SP', 'Качество_кода_%']].copy()
    df_plot = df_plot.dropna().reset_index(drop=True)

    fig = px.scatter(
        df_plot,
        x='Velocity_SP',
        y='Качество_кода_%',
        labels={
            'Velocity_SP': 'Velocity (Story Points)',
            'Качество_кода_%': 'Качество кода (%)'
        }
    )

    fig.update_traces(marker=dict(size=10, line=dict(width=2, color='DarkSlateGrey')))
    fig.update_layout(template='plotly_white')

    return fig



# График 5: Таблица
@app.callback(
    Output('data-table', 'children'),
    [Input('period-dropdown', 'value'),
     Input('phase-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_table(period, phases, upload_contents):
    if df_global is None:
        return html.Div("Загрузите данные для отображения таблицы", className="alert alert-info")

    df_filtered = filter_data(df_global, period, phases)

    if df_filtered.empty:
        return html.Div("Нет данных для выбранных фильтров", className="alert alert-warning")

    # Выбор ключевых колонок для отображения
    display_columns = ['Месяц', 'Завершенные_задачи', 'Velocity_SP', 
                      'Качество_кода_%', 'Баги_исправлено', 'Категория_фазы']

    df_display = df_filtered[[col for col in display_columns if col in df_filtered.columns]]

    table = dash_table.DataTable(
        data=df_display.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df_display.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'font-family': 'Arial'
        },
        style_header={
            'backgroundColor': '#2E86AB',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ],
        page_size=10
    )

    return table


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
