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
        
        # Limpieza profunda de datos
        # 1. Eliminar columnas completamente nulas
        df = df.dropna(axis=1, how='all')
        
        # 2. Eliminar filas completamente nulas
        df = df.dropna(axis=0, how='all')
        
        # 3. Eliminar columnas Unnamed
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        # 4. Eliminar columnas vacías (solo espacios)
        df = df.loc[:, df.columns.str.strip() != '']
        
        # 5. Eliminar columnas con 100% valores faltantes
        missing_pct = df.isna().sum() / len(df) * 100
        cols_to_keep = missing_pct[missing_pct < 100].index
        df = df[cols_to_keep]
        
        return df
    except FileNotFoundError:
        return None

@lru_cache(maxsize=1)
def cargar_datos_raw(filepath: Optional[str] = None) -> Optional[pd.DataFrame]:
    path = Path(filepath) if filepath else RAW_DATA_PATH
    try:
        df = pd.read_csv(path, index_col='DateTime', parse_dates=['DateTime'])
        
        # Limpieza profunda de datos
        # 1. Eliminar columnas completamente nulas
        df = df.dropna(axis=1, how='all')
        
        # 2. Eliminar filas completamente nulas
        df = df.dropna(axis=0, how='all')
        
        # 3. Eliminar columnas Unnamed
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        # 4. Eliminar columnas vacías (solo espacios)
        df = df.loc[:, df.columns.str.strip() != '']
        
        # 5. Eliminar columnas con 100% valores faltantes
        missing_pct = df.isna().sum() / len(df) * 100
        cols_to_keep = missing_pct[missing_pct < 100].index
        df = df[cols_to_keep]
        
        return df
    except FileNotFoundError:
        return None

@lru_cache(maxsize=1)
def cargar_reporte_missings(filepath: Optional[str] = None) -> Optional[pd.DataFrame]:
    path = Path(filepath) if filepath else MISSING_REPORT_PATH
    try:
        df = pd.read_csv(path)
        
        # Limpieza del reporte de missings
        # 1. Eliminar filas sin nombre de columna
        if 'Column' in df.columns:
            df = df[df['Column'].notna()].copy()
            df = df[~df['Column'].str.contains('^Unnamed', na=False)].copy()
            df = df[df['Column'].str.strip() != ''].copy()
        elif 'Variable' in df.columns:
            df = df[df['Variable'].notna()].copy()
            df = df[~df['Variable'].str.contains('^Unnamed', na=False)].copy()
            df = df[df['Variable'].str.strip() != ''].copy()
        
        # 2. Eliminar columnas con 100% missing (Raw_Missing_% o Missing Percentage)
        if 'Raw_Missing_%' in df.columns:
            df = df[df['Raw_Missing_%'] < 100].copy()
        elif 'Missing Percentage' in df.columns:
            df = df[df['Missing Percentage'] < 100].copy()
        
        return df
    except FileNotFoundError:
        return None