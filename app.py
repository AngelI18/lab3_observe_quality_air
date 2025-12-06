import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.loader import cargar_datos_limpios, cargar_reporte_missings, cargar_datos_raw
from src.plots import configurar_estilo
from src.config import DatasetConfig, TabConfig
from src.plot_builder import PlotFactory

st.set_page_config(page_title="Lab 3: Air Quality Analysis", layout="wide")
configurar_estilo()

# ============ INICIALIZACIÓN DE DATOS (Inyección de Dependencias) ============
@st.cache_data
def cargar_datos_con_cache():
    return cargar_datos_limpios()

@st.cache_data
def cargar_raw_con_cache():
    return cargar_datos_raw()

@st.cache_data
def cargar_missings_con_cache():
    return cargar_reporte_missings()

df_completo = cargar_datos_con_cache()
df_raw = cargar_raw_con_cache()
df_missings = cargar_missings_con_cache()

if df_completo is None:
    st.error("Datos no encontrados. Ejecuta el notebook de limpieza primero.")
    st.stop()

# ============ CONFIGURACIÓN CENTRALIZADA ============
dataset_config = DatasetConfig()
tab_config = TabConfig()

# Filtrar columnas según configuración para tabs 1 y 2
df = dataset_config.filter_columns(df_completo)
if df_raw is not None:
    df_raw = dataset_config.filter_columns_raw(df_raw)

st.sidebar.title("Panel de Control")
st.sidebar.info("Ajusta los parámetros de visualización.")

# Botón para limpiar caché y recargar datos
if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()
    st.rerun()

st.title("Dashboard de Calidad del Aire")

tab1, tab2, tab3 = st.tabs(["Distribuciones y Outliers", "Análisis de Correlación", "Comparativa Raw vs Clean"])

# ============ TAB 1: DISTRIBUCIONES Y OUTLIERS ============
with tab1:
    st.header("Análisis Univariable")
    
    col_izq, col_der = st.columns([1, 2])
    
    # Panel de controles (Mutable)
    with col_izq:
        st.subheader("Configuración Histograma")
        var_hist = st.selectbox("Variable a analizar:", df.columns.tolist(), index=0)
        
        # Actualizamos configuración dinámicamente
        bins = st.slider("Cantidad de Bins:", 5, 100, tab_config.get_histogram_config().bins)
        color_hist = st.color_picker("Color del gráfico:", tab_config.get_histogram_config().color)
        escala_log = st.checkbox("Escala Logarítmica (eje Y)", value=tab_config.get_histogram_config().log_scale)
        
        # Actualizar config
        tab_config.update_histogram(bins=bins, color=color_hist, log_scale=escala_log)
        
    # Construcción del gráfico (Desacoplada)
    with col_der:
        hist_builder = PlotFactory.create_histogram_builder(df, tab_config.get_histogram_config())
        sample_len = df[var_hist].dropna().shape[0]
        altura_hist = max(450, min(900, 300 + sample_len // 400))
        tab_config.update_histogram(height=altura_hist)
        
        fig_hist = hist_builder.build(var_hist)
        st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()
    
    # Boxplots
    st.subheader("Comparación de Outliers (Boxplots)")
    st.markdown("Selecciona múltiples variables para compararlas lado a lado:")

    cols_default = ['CO(GT)', 'PT08.S1(CO)', 'NOx(GT)']
    cols_default = [c for c in cols_default if c in df.columns]
    vars_box = st.multiselect("Variables:", df.columns.tolist(), default=cols_default)
    log_box = st.checkbox("Escala logarítmica en boxplots", value=tab_config.get_boxplot_config().log_scale)
    
    tab_config.update_boxplot(log_scale=log_box)
    
    box_builder = PlotFactory.create_boxplot_builder(df, tab_config.get_boxplot_config())
    fig_box = box_builder.build(vars_box)
    st.plotly_chart(fig_box, use_container_width=True)
    
    if not vars_box:
        st.info("Selecciona al menos una variable para visualizar.")

# ============ TAB 2: ANÁLISIS BIVARIABLE ============
with tab2:
    st.header("Análisis Bivariable")

    c1, c2, c3, c4 = st.columns(4)
    
    # Filtrar variables GT (referencias reales) y PT08 (sensores)
    vars_gt = [col for col in df.columns if '(GT)' in col]
    vars_pt08 = [col for col in df.columns if 'PT08.' in col]
    
    x_axis = c1.selectbox("Eje X (Referencia):", vars_gt, index=0 if vars_gt else None)
    y_axis = c2.selectbox("Eje Y (Sensor):", vars_pt08, index=0 if vars_pt08 else None)
    color_var = c3.selectbox("Colorear por:", ['Ninguno'] + vars_gt + vars_pt08, index=0)

    alpha_val = st.sidebar.slider("Transparencia", 0.1, 1.0, tab_config.get_scatter_config().alpha)
    size_val = st.sidebar.slider("Tamaño de Puntos", 2, 20, tab_config.get_scatter_config().size)
    
    tab_config.update_scatter(alpha=alpha_val, size=size_val)
    
    st.markdown(f"**Visualización:** `{x_axis}` vs `{y_axis}`")
    
    scatter_builder = PlotFactory.create_scatter_builder(df, tab_config.get_scatter_config())
    fig_scatter = scatter_builder.build(x_axis, y_axis, color_var)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    if x_axis != y_axis:
        corr_val = df[[x_axis, y_axis]].corr().iloc[0, 1]
        st.metric("Coeficiente de Correlación (Pearson)", f"{corr_val:.4f}")
    else:
        st.info("Selecciona variables distintas para calcular correlación.")

    st.divider()
    st.subheader("Heatmap de Correlación")
    columnas_recom = ['CO(GT)','PT08.S1(CO)', 'C6H6(GT)','PT08.S2(NMHC)','NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)', 'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
    cols_heatmap = st.multiselect("Columnas para el heatmap:", df.columns.tolist(), default=[c for c in columnas_recom if c in df.columns])
    
    heatmap_builder = PlotFactory.create_heatmap_builder(df, tab_config.get_heatmap_config())
    fig_heatmap = heatmap_builder.build(cols_heatmap)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    if len(cols_heatmap) < 2:
        st.info("Selecciona al menos dos columnas para el heatmap.")

# ============ TAB 3: COMPARATIVA RAW VS CLEAN ============
with tab3:
    st.header("Comparativa: Dataset Raw vs Clean")
    st.markdown("Análisis de datos faltantes antes y después del procesamiento.")
    
    if df_raw is not None and df_missings is not None:
        # Diagnóstico de Calidad de Datos
        st.subheader("📊 Diagnóstico de Calidad de Datos")
        
        missing_builder = PlotFactory.create_missing_data_builder(df_missings)
        fig_missing = missing_builder.build(umbral_critico=90.0)
        st.plotly_chart(fig_missing, use_container_width=True)
        
        st.divider()
        
        # Resumen de Calidad de Datos
        st.subheader("📋 Resumen de Calidad de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Filas Raw (Original)", len(df_raw))
            st.metric("Filas Clean (Procesado)", len(df_completo))
        
        with col2:
            st.metric("Columnas Raw", len(df_raw.columns))
            st.metric("Columnas Clean", len(df_completo.columns))
        
        with st.expander("Ver Tabla Completa de Missing Values"):
            st.dataframe(df_missings, use_container_width=True)
    else:
        st.warning("No se encontraron los datos necesarios para la comparación.")