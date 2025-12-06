import pandas as pd
from pathlib import Path
from typing import Optional
from functools import lru_cache

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / 'Data' / 'processed'
DATA_DIR_RAW = ROOT_DIR / 'Data' / 'raw'
CLEANED_DATA_PATH = DATA_DIR / 'air_quality_UCI_cleaned.csv'
MISSING_REPORT_PATH = DATA_DIR / 'missing_values_summary.csv'
RAW_DATA_PATH = DATA_DIR_RAW / 'AirQualityUCI_cleaned_columns_and_rows_any.csv'

# Función auxiliar para limpiar caché si es necesario
def clear_cache():
    """Limpia el caché de todas las funciones de carga."""
    cargar_datos_limpios.cache_clear()
    cargar_datos_raw.cache_clear()
    cargar_reporte_missings.cache_clear()

@lru_cache(maxsize=1)
def cargar_datos_limpios(filepath: Optional[str] = None) -> Optional[pd.DataFrame]:
    path = Path(filepath) if filepath else CLEANED_DATA_PATH
    try:
        df = pd.read_csv(path, index_col='DateTime', parse_dates=['DateTime'])
        return df
    except FileNotFoundError:
        return None

@lru_cache(maxsize=1)
def cargar_datos_raw(filepath: Optional[str] = None) -> Optional[pd.DataFrame]:
    path = Path(filepath) if filepath else RAW_DATA_PATH
    try:
        df = pd.read_csv(path, index_col='DateTime', parse_dates=['DateTime'])
        return df
    except FileNotFoundError:
        return None

@lru_cache(maxsize=1)
def cargar_reporte_missings(filepath: Optional[str] = None) -> Optional[pd.DataFrame]:
    path = Path(filepath) if filepath else MISSING_REPORT_PATH
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return None