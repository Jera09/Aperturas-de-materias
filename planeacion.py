import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial
st.set_page_config(
    page_title="Programación de aperturas de materias",
    layout="wide",
    page_icon="A.png"
)

st.image("A.png", width=200)


# ==========================================
# 2. CARGA Y SANITIZACIÓN DE DATOS (DATA LOGIC)
# ==========================================
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Analisis de materias.xlsx", engine="openpyxl")
    columnas_texto = ["Coordinador", "área de conocimiento", "Materia", "Recomendación"]
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    return df

df = cargar_datos()

# ==========================================
# 3. BARRA LATERAL (FILTROS)
# ==========================================
st.sidebar.title("Filtros de visualización")
st.sidebar.markdown("Selecciona el área de conocimiento para revisar la apertura de materias.")

areas = [a for a in df["área de conocimiento"].dropna().unique() if a != 'nan']

area_seleccionada = st.sidebar.multiselect("📚 Filtrar por Área", areas, placeholder="Todas las áreas")

# Aplicar lógica de filtrado jerárquico
df_filtrado = df.copy()

if area_seleccionada:
    df_filtrado = df_filtrado[df_filtrado["área de conocimiento"].isin(area_seleccionada)]


st.header("Apertura de materias")
st.subheader("Identifica visualmente la carga de materias programadas por cada ciclo escolar.")
    
# Identificar columnas con formato de año/semestre (ej. Primavera 2026)
columnas_semestres = [col for col in df.columns if "202" in str(col)]
    
if len(df_filtrado) > 0 and columnas_semestres:
    # Transformar datos para el mapa de calor (1 si está planeada, 0 si no)
    df_heat = df_filtrado[['Materia'] + columnas_semestres].copy()
    df_heat.set_index('Materia', inplace=True)
    df_heat = df_heat.notna().astype(int)
        

    # ---------------------------------------------------------------
    st.warning("⚠️ **La apertura de materias dependerá de la demanda de alumnos**")       
    # Alerta UX si la lista es excesivamente larga
    if len(df_heat) > 25:
        st.warning("⚠️ **Recomendación:** Hay demasiadas materias en pantalla para un análisis cómodo. Filtra por 'Área' en el menú de la izquierda para limpiar la vista.")
            
    fig_heat = px.imshow(
        df_heat,
        labels=dict(x="Ciclo / Semestre", y="Materia", color="Planificado"),
        x=columnas_semestres,
        y=df_heat.index,
        color_continuous_scale=[[0, '#eaedf0'], [1, '#1ebd8c']], # Gris neutro para no ofertado, verde brillante para ofertado
        aspect="auto"
    )
    fig_heat.update_traces(xgap=3, ygap=3)
    fig_heat.update_xaxes(side="top", tickangle=-30)
    fig_heat.update_layout(
        coloraxis_showscale=False,
        margin=dict(t=60, l=0, r=0, b=0),
        height=max(350, len(df_heat) * 28) # Calcula dinámicamente la altura
    )
        
    # Tip de UX para enseñarles a descargar la imagen
    st.caption("💡 **Tip:** Pasa el ratón sobre la esquina superior derecha del gráfico y haz clic en el ícono de la cámara 📷 para descargar esta visualización como imagen.")
        
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Ajusta los filtros para visualizar la proyección de semestres.")
