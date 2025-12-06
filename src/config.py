"""
Configuración centralizada de la aplicación.
Sigue el principio Single Responsibility: cada cambio afecta solo este módulo.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class HistogramConfig:
    """Configuración para histogramas."""
    bins: int = 30
    color: str = "#4C72B0"
    log_scale: bool = False
    height: int = 600
    

@dataclass
class BoxplotConfig:
    """Configuración para boxplots."""
    log_scale: bool = False
    height: int = 700


@dataclass
class ScatterConfig:
    """Configuración para scatter plots."""
    alpha: float = 0.5
    size: int = 5
    height: int = 800


@dataclass
class HeatmapConfig:
    """Configuración para heatmaps."""
    height: int = 600


@dataclass
class ImputationComparisonConfig:
    """Configuración para comparación de imputación."""
    sample_days: int = 30
    show_grid: bool = True
    figsize: tuple = (12, 6)


@dataclass
class DatasetConfig:
    """Configuración de datos permitidos."""
    columns_permitidas: List[str] = field(default_factory=lambda: [
        'CO(GT)', 'PT08.S1(CO)', 'C6H6(GT)', 'PT08.S2(NMHC)',
        'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)', 'PT08.S4(NO2)',
        'PT08.S5(O3)', 'T', 'RH', 'AH'
    ])
    columns_raw_extra: List[str] = field(default_factory=lambda: ['NMHC(GT)'])

    def get_columns_para_raw(self) -> List[str]:
        """Retorna las columnas permitidas para raw (incluye extra)."""
        return self.columns_permitidas + self.columns_raw_extra

    def filter_columns(self, df):
        """Filtra el DataFrame para mantener solo columnas permitidas (mutable)."""
        cols_validas = [col for col in self.columns_permitidas if col in df.columns]
        return df[cols_validas]

    def filter_columns_raw(self, df):
        """Filtra el DataFrame raw para mantener solo columnas permitidas."""
        cols_validas = [col for col in self.get_columns_para_raw() if col in df.columns]
        return df[cols_validas]


class TabConfig:
    """Configuración mutable para cada tab de visualización."""
    
    def __init__(self):
        self.tab1_config = {
            'histogram': HistogramConfig(),
            'boxplot': BoxplotConfig(),
        }
        self.tab2_config = {
            'scatter': ScatterConfig(),
            'heatmap': HeatmapConfig(),
        }
        self.tab3_config = {
            'imputation': ImputationComparisonConfig(),
        }

    def update_histogram(self, **kwargs):
        """Permite actualizar configuración de histograma."""
        for key, value in kwargs.items():
            if hasattr(self.tab1_config['histogram'], key):
                setattr(self.tab1_config['histogram'], key, value)

    def update_boxplot(self, **kwargs):
        """Permite actualizar configuración de boxplot."""
        for key, value in kwargs.items():
            if hasattr(self.tab1_config['boxplot'], key):
                setattr(self.tab1_config['boxplot'], key, value)

    def update_scatter(self, **kwargs):
        """Permite actualizar configuración de scatter."""
        for key, value in kwargs.items():
            if hasattr(self.tab2_config['scatter'], key):
                setattr(self.tab2_config['scatter'], key, value)

    def update_heatmap(self, **kwargs):
        """Permite actualizar configuración de heatmap."""
        for key, value in kwargs.items():
            if hasattr(self.tab2_config['heatmap'], key):
                setattr(self.tab2_config['heatmap'], key, value)

    def update_imputation(self, **kwargs):
        """Permite actualizar configuración de comparación de imputación."""
        for key, value in kwargs.items():
            if hasattr(self.tab3_config['imputation'], key):
                setattr(self.tab3_config['imputation'], key, value)

    def get_histogram_config(self) -> HistogramConfig:
        return self.tab1_config['histogram']

    def get_boxplot_config(self) -> BoxplotConfig:
        return self.tab1_config['boxplot']

    def get_scatter_config(self) -> ScatterConfig:
        return self.tab2_config['scatter']

    def get_heatmap_config(self) -> HeatmapConfig:
        return self.tab2_config['heatmap']

    def get_imputation_config(self) -> ImputationComparisonConfig:
        return self.tab3_config['imputation']
