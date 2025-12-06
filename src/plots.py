import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional
import pandas as pd

class PlotConfigurator:
    @staticmethod
    def aplicar_tema_defecto():
        sns.set_theme(style="whitegrid", context="notebook")

def configurar_estilo():
    PlotConfigurator.aplicar_tema_defecto()

def plot_missing_bars(missings_df: pd.DataFrame, umbral_critico: float = 90.0):
    if missings_df is None or missings_df.empty:
        return go.Figure()
    
    # Adaptar el DataFrame según su estructura
    df_plot = missings_df.copy()
    
    # Si tiene la estructura del reporte (Column, Raw_Missing_%, etc.)
    if 'Column' in df_plot.columns and 'Raw_Missing_%' in df_plot.columns:
        df_plot = df_plot.rename(columns={'Column': 'Variable', 'Raw_Missing_%': 'Missing Percentage'})
    # Si tiene estructura antigua (Variable, Missing Percentage)
    elif 'Variable' not in df_plot.columns or 'Missing Percentage' not in df_plot.columns:
        # Intentar interpretar el formato genérico
        if df_plot.columns[0] not in ['Variable', 'Missing Percentage']:
            df_plot = df_plot.reset_index()
            df_plot.columns = ['Variable', 'Missing Percentage']
    
    fig = px.bar(
        df_plot,
        x='Variable',
        y='Missing Percentage',
        title='Diagnóstico de Calidad de Datos',
        labels={'Missing Percentage': '% Nulos'},
        color='Missing Percentage',
        color_continuous_scale='Reds'
    )
    fig.add_hline(
        y=umbral_critico,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Crítico ({umbral_critico}%)",
        annotation_position="top right"
    )
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_tickangle=-45,
        height=max(400, 60 * len(df_plot))
    )
    return fig

def plot_multiple_boxplots(df: pd.DataFrame, columnas: List[str], log_scale: bool = False):
    if not columnas:
        return go.Figure()
    data_melted = df[columnas].melt(var_name='Variable', value_name='Valor')
    fig = px.box(
        data_melted,
        x='Variable',
        y='Valor',
        title='Comparación de Distribuciones y Outliers',
        color='Variable',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        points='outliers'
    )
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Valor: %{y}<br>Q1: %{q1}<br>Mediana: %{median}<br>Q3: %{q3}<extra></extra>'
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        xaxis_title='Variable',
        yaxis_title='Valor',
        height=max(700, 300 + 180 * len(columnas)),
        boxmode='group',
        margin=dict(t=60, b=60, l=60, r=20)
    )
    fig.update_yaxes(rangemode='tozero')
    if log_scale:
        fig.update_yaxes(type='log')
    return fig

def plot_custom_histogram(
    df: pd.DataFrame, 
    columna: str, 
    bins: int = 30, 
    color: str = '#1f77b4', 
    log_scale: bool = False,
    height: Optional[int] = None
):
    serie = df[columna].dropna()
    if serie.empty:
        return go.Figure()
    
    nbins = bins if bins else min(80, max(10, int(len(serie) ** 0.5)))
    
    # Crear figura vacía
    fig = go.Figure()
    
    # Calcular histograma manualmente
    try:
        import numpy as np
        counts, bin_edges = np.histogram(serie, bins=nbins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Añadir barras del histograma
        fig.add_trace(go.Bar(
            x=bin_centers,
            y=counts,
            name='Frecuencia',
            marker=dict(
                color=color,
                line=dict(color='black', width=1)
            ),
            hovertemplate='<b>Rango: %{x:.2f}</b><br>Frecuencia: %{y}<extra></extra>',
            width=(bin_edges[1] - bin_edges[0]) * 0.9
        ))
        
        # Calcular KDE para la línea de densidad
        try:
            from scipy import stats
            
            kde = stats.gaussian_kde(serie)
            x_range = np.linspace(serie.min(), serie.max(), 200)
            kde_values = kde(x_range)
            
            # Escalar KDE a la altura del histograma
            hist_max = counts.max()
            kde_scaled = kde_values * hist_max / kde_values.max()
            
            # Añadir línea KDE
            fig.add_trace(go.Scatter(
                x=x_range,
                y=kde_scaled,
                mode='lines',
                name='Densidad',
                line=dict(color='darkblue', width=2.5),
                hovertemplate='<b>Densidad</b><br>Valor: %{x:.2f}<extra></extra>'
            ))
        except ImportError:
            pass
            
    except Exception:
        # Fallback a histograma básico
        fig = px.histogram(
            serie, 
            x=columna, 
            nbins=nbins,
            color_discrete_sequence=[color]
        )
        fig.update_traces(
            marker=dict(line=dict(color='black', width=1))
        )
    
    if log_scale:
        fig.update_yaxes(type='log', title='Frecuencia (Log)')
    
    fig.update_layout(
        title=f"Distribución de {columna}",
        hovermode='x unified',
        plot_bgcolor='white',
        xaxis_title=columna,
        yaxis_title='Frecuencia',
        height=height or max(600, min(950, 400 + len(serie) // 300)),
        showlegend=True,
        bargap=0.1
    )
    
    return fig

def plot_interactive_scatter(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    color_col: Optional[str] = None, 
    alpha: float = 0.5, 
    size: int = 5,
    height: int = 720
):
    use_color = color_col if color_col != 'Ninguno' else None
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col,
        color=use_color,
        title=f'Correlación: {x_col} vs {y_col}',
        opacity=alpha,
        color_continuous_scale='Magma' if use_color else None
    )
    fig.update_traces(
        marker=dict(size=size),
        hovertemplate=f'<b>{x_col}:</b> %{{x}}<br><b>{y_col}:</b> %{{y}}<extra></extra>'
    )
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=height
    )
    return fig


def plot_heatmap(df: pd.DataFrame, columnas: List[str]):
    if not columnas or len(columnas) < 2:
        return go.Figure()
    matriz = df[columnas].corr()
    fig = px.imshow(
        matriz,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect='auto',
        title='Matriz de Correlación'
    )
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title='Variables',
        yaxis_title='Variables',
        height=max(500, 80 * len(columnas))
    )
    return fig


def plot_comparacion_imputacion(df_clean: pd.DataFrame, df_raw: pd.DataFrame, columna: str, 
                                fecha_inicio = None, fecha_fin = None):
    """
    Grafica la serie de tiempo comparando datos originales vs interpolados.
    Muestra valores reales como puntos azules y valores interpolados como línea roja.
    """
    # Filtramos por fecha si se especifica (para hacer zoom y ver los detalles)
    if fecha_inicio is not None and fecha_fin is not None:
        clean_segment = df_clean.loc[fecha_inicio:fecha_fin]
        raw_segment = df_raw.loc[fecha_inicio:fecha_fin]
    else:
        # Si no, tomamos las primeras ~744 horas (1 mes) para que no sea muy pesado
        clean_segment = df_clean.iloc[:744]
        raw_segment = df_raw.iloc[:744]

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 1. Datos Interpolados (Línea roja continua)
    ax.plot(clean_segment.index, clean_segment[columna], 
            color='red', label='Interpolado (Relleno)', alpha=0.6, linewidth=2)
    
    # 2. Datos Crudos Originales (Puntos azules)
    # Donde NO haya puntos azules, significa que ahí había un valor faltante
    if columna in raw_segment.columns:
        # Filtrar solo los valores NO nulos del raw
        raw_no_nulos = raw_segment[raw_segment[columna].notna()]
        ax.scatter(raw_no_nulos.index, raw_no_nulos[columna], 
                  color='blue', label='Dato Original (Raw)', s=30, zorder=10, alpha=0.8)
    
    ax.set_title(f"Impacto de la Interpolación: {columna}", fontsize=14, fontweight='bold')
    ax.set_xlabel("Fecha/Hora", fontsize=11)
    ax.set_ylabel("Valor", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig