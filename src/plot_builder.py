"""
Abstracción de visualizaciones desacoplada.
Sigue los principios SOLID: cada tipo de visualización es independiente y modificable.
"""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any, Union
from matplotlib.figure import Figure as MatplotlibFigure
from .plots import (
    plot_custom_histogram,
    plot_multiple_boxplots,
    plot_interactive_scatter,
    plot_heatmap,
    plot_missing_bars,
    plot_comparacion_imputacion
)
from .config import (
    HistogramConfig,
    BoxplotConfig,
    ScatterConfig,
    HeatmapConfig,
    ImputationComparisonConfig
)


class PlotBuilder(ABC):
    """Interfaz base para constructores de plots (Open/Closed Principle)."""
    
    @abstractmethod
    def build(self, *args, **kwargs) -> Union[go.Figure, MatplotlibFigure]:
        """Construye y retorna un gráfico Plotly o Matplotlib."""
        pass


class HistogramBuilder(PlotBuilder):
    """Constructor para histogramas (Dependency Inversion)."""
    
    def __init__(self, df: pd.DataFrame, config: HistogramConfig):
        self.df = df
        self.config = config
    
    def build(self, column: str, **kwargs) -> go.Figure:
        """Construye histograma con configuración personalizable."""
        # Actualizar config si hay parámetros adicionales
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        return plot_custom_histogram(
            self.df,
            column,
            self.config.bins,
            self.config.color,
            self.config.log_scale,
            height=self.config.height
        )


class BoxplotBuilder(PlotBuilder):
    """Constructor para boxplots."""
    
    def __init__(self, df: pd.DataFrame, config: BoxplotConfig):
        self.df = df
        self.config = config
    
    def build(self, columns: List[str], **kwargs) -> go.Figure:
        """Construye boxplots con configuración personalizable."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        if not columns:
            return go.Figure()
        
        return plot_multiple_boxplots(
            self.df,
            columns,
            log_scale=self.config.log_scale
        )


class ScatterBuilder(PlotBuilder):
    """Constructor para scatter plots."""
    
    def __init__(self, df: pd.DataFrame, config: ScatterConfig):
        self.df = df
        self.config = config
    
    def build(self, x_col: str, y_col: str, color_col: str = 'Ninguno', **kwargs) -> go.Figure:
        """Construye scatter plot con configuración personalizable."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        if x_col == y_col:
            return go.Figure()
        
        return plot_interactive_scatter(
            self.df,
            x_col,
            y_col,
            color_col if color_col != 'Ninguno' else None,
            self.config.alpha,
            self.config.size,
            height=self.config.height
        )


class HeatmapBuilder(PlotBuilder):
    """Constructor para heatmaps."""
    
    def __init__(self, df: pd.DataFrame, config: HeatmapConfig):
        self.df = df
        self.config = config
    
    def build(self, columns: List[str], **kwargs) -> go.Figure:
        """Construye heatmap con configuración personalizable."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        if len(columns) < 2:
            return go.Figure()
        
        return plot_heatmap(self.df, columns)


class MissingDataBuilder(PlotBuilder):
    """Constructor para gráficos de datos faltantes."""
    
    def __init__(self, df_missings: pd.DataFrame):
        self.df_missings = df_missings
    
    def build(self, umbral_critico: float = 90.0, **kwargs) -> go.Figure:
        """Construye gráfico de datos faltantes."""
        if self.df_missings is None or self.df_missings.empty:
            return go.Figure()
        
        return plot_missing_bars(self.df_missings, umbral_critico)


class ImputationComparisonBuilder(PlotBuilder):
    """Constructor para comparación de imputación."""
    
    def __init__(self, df_clean: pd.DataFrame, df_raw: pd.DataFrame, config: ImputationComparisonConfig):
        self.df_clean = df_clean
        self.df_raw = df_raw
        self.config = config
    
    def build(self, columna: str, fecha_inicio=None, fecha_fin=None, **kwargs):
        """Construye gráfico de comparación de imputación."""
        # Actualizar config si hay parámetros adicionales
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        return plot_comparacion_imputacion(
            self.df_clean,
            self.df_raw,
            columna,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )


class PlotFactory:
    """Factory que crea builders según el tipo (Factory Pattern)."""
    
    @staticmethod
    def create_histogram_builder(df: pd.DataFrame, config: HistogramConfig) -> HistogramBuilder:
        return HistogramBuilder(df, config)
    
    @staticmethod
    def create_boxplot_builder(df: pd.DataFrame, config: BoxplotConfig) -> BoxplotBuilder:
        return BoxplotBuilder(df, config)
    
    @staticmethod
    def create_scatter_builder(df: pd.DataFrame, config: ScatterConfig) -> ScatterBuilder:
        return ScatterBuilder(df, config)
    
    @staticmethod
    def create_heatmap_builder(df: pd.DataFrame, config: HeatmapConfig) -> HeatmapBuilder:
        return HeatmapBuilder(df, config)
    
    @staticmethod
    def create_missing_data_builder(df_missings: pd.DataFrame) -> MissingDataBuilder:
        return MissingDataBuilder(df_missings)
    
    @staticmethod
    def create_imputation_comparison_builder(df_clean: pd.DataFrame, df_raw: pd.DataFrame, 
                                             config: ImputationComparisonConfig) -> ImputationComparisonBuilder:
        return ImputationComparisonBuilder(df_clean, df_raw, config)

    @staticmethod
    def create_regression_plot(df, sensor, gt):
        return RegressionBuilder(df, sensor, gt).build()

    @staticmethod
    def create_multivariable_regression_plot(df, target, predictors):
        return MultivariableRegressionBuilder(df, target, predictors).build()

    @staticmethod
    def create_drift_plot(df, sensor, gt):
        return DriftBuilder(df, sensor, gt).build()


class RegressionBuilder(PlotBuilder):
    """Regresión univariable lineal para Modelamiento I."""
    
    def __init__(self, df: pd.DataFrame, sensor: str, gt: str):
        self.df = df
        self.sensor = sensor
        self.gt = gt
    
    def build(self) -> go.Figure:
        import numpy as np
        
        data = self.df[[self.sensor, self.gt]].dropna()
        x = data[self.sensor].to_numpy()
        y = data[self.gt].to_numpy()

        # Ajuste lineal
        a, b = np.polyfit(x, y, 1)
        y_pred = a * x + b
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=y, mode='markers', name='Datos', opacity=0.6
        ))
        xx = np.linspace(x.min(), x.max(), 200)
        fig.add_trace(go.Scatter(
            x=xx, y=a*xx + b, mode='lines', name='Ajuste lineal', line=dict(color='red')
        ))

        fig.update_layout(
            title=f"{self.sensor} → {self.gt} (Modelo lineal)",
            xaxis_title=self.sensor,
            yaxis_title=self.gt
        )
        return fig


class MultivariableRegressionBuilder(PlotBuilder):
    """Regresión multivariable lineal para CO(GT)."""
    
    def __init__(self, df: pd.DataFrame, target: str, predictors: list):
        self.df = df
        self.target = target
        self.predictors = predictors
    
    def build(self):
        import numpy as np
        
        df_mv = self.df[self.predictors + [self.target]].dropna()
        X = df_mv[self.predictors].to_numpy()
        X_design = np.hstack([X, np.ones((X.shape[0], 1))])
        y = df_mv[self.target].to_numpy()

        coeffs, *_ = np.linalg.lstsq(X_design, y, rcond=None)
        y_pred = X_design @ coeffs

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=y, y=y_pred, mode="markers", opacity=0.6,
            name="Observado vs Predicho"
        ))

        minv, maxv = min(y.min(), y_pred.min()), max(y.max(), y_pred.max())
        fig.add_trace(go.Scatter(
            x=[minv, maxv], y=[minv, maxv],
            mode="lines", name="Línea ideal", line=dict(color="red")
        ))

        fig.update_layout(
            title=f"Modelo Multivariable: {self.target}",
            xaxis_title="Observado",
            yaxis_title="Predicho"
        )
        return fig

class DriftBuilder(PlotBuilder):
    """Análisis del cambio de pendiente en el tiempo."""
    
    def __init__(self, df: pd.DataFrame, sensor: str, gt: str):
        self.df = df
        self.sensor = sensor
        self.gt = gt
    
    def build(self):
        import numpy as np
        
        df_temp = self.df[[self.sensor, self.gt]].dropna().resample("ME")
        slopes, dates = [], []

        for period, grp in df_temp:
            if len(grp) < 20:
                continue

            x = grp[self.sensor].to_numpy()
            y = grp[self.gt].to_numpy()
            
            a, b = np.polyfit(x, y, 1)
            slopes.append(a)
            dates.append(period)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=slopes, mode="lines+markers",
            name="Pendiente mensual"
        ))

        fig.update_layout(
            title=f"Drift del sensor {self.sensor}",
            xaxis_title="Fecha",
            yaxis_title="Pendiente"
        )
        return fig
