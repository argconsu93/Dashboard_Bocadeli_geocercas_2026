import streamlit as st
import pandas as pd
import json
import os
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard Bocadeli - SV Centro", layout="wide")

# CARPETA Y RUTAS DE DATOS EN LA NUBE
DATA_DIR = "data_nube"
os.makedirs(DATA_DIR, exist_ok=True)
csv_path = os.path.join(DATA_DIR, "SVCentro_Grupos_actualizado.csv")
geojson_path = os.path.join(DATA_DIR, "Geocercas_SVCentro.geojson")

# LISTADO DE USUARIOS Y ROLES
USUARIOS_ROLES = [
    {"nombre": "JORGE LUIS PINEDA", "rol": "Supervisor", "grupo": "GRUPO_01", "pass": "G01"},
    {"nombre": "OSCAR ANTONIO DEL CID", "rol": "Supervisor", "grupo": "GRUPO_02", "pass": "G02"},
    {"nombre": "RICARDO ERNESTO RIVAS", "rol": "Supervisor", "grupo": "GRUPO_03", "pass": "G03"},
    {"nombre": "NOE ALBERTO CORNEJO", "rol": "Supervisor", "grupo": "GRUPO_04", "pass": "G04"},
    {"nombre": "CHRISTIAN CORTEZ", "rol": "Supervisor", "grupo": "GRUPO_05", "pass": "G05"},
    {"nombre": "JAIME NAVARRO", "rol": "Supervisor", "grupo": "GRUPO_06", "pass": "G06"},
    {"nombre": "RUBEN OCEAS HERNANDEZ", "rol": "Supervisor", "grupo": "GRUPO_07", "pass": "G07"},
    {"nombre": "EDWIN ADONAY GALEAS", "rol": "Supervisor", "grupo": "GRUPO_08", "pass": "G08"},
    {"nombre": "LUIS ALFREDO LOPEZ", "rol": "Supervisor", "grupo": "GRUPO_09", "pass": "G09"},
    {"nombre": "MANUEL ANTONIO ORELLANA", "rol": "Supervisor", "grupo": "GRUPO_10", "pass": "G10"},
    {"nombre": "NOE HERNANDEZ", "rol": "Jefatura", "grupo": "TODOS", "pass": "BOCADELI"},
    {"nombre": "ALVARO CAMPOS", "rol": "Jefatura", "grupo": "TODOS", "pass": "BOCADELI"},
    {"nombre": "JESSICA MEJIA", "rol": "Jefatura", "grupo": "TODOS", "pass": "BOCADELI"},
    {"nombre": "WILBER MERCADO", "rol": "Jefatura", "grupo": "TODOS", "pass": "BOCADELI"},
    {"nombre": "ISRAEL CONSUEGRA", "rol": "Administrador", "grupo": "TODOS", "pass": "SVCENTRO"},
    {"nombre": "PAOLA CASTANEDA", "rol": "Analista", "grupo": "TODOS", "pass": "SVCENTRO"},
    {"nombre": "ALDAHIR RODRIGUEZ", "rol": "Analista", "grupo": "TODOS", "pass": "SVCENTRO"},
    {"nombre": "RENE DOMINGUEZ", "rol": "Analista", "grupo": "TODOS", "pass": "SVCENTRO"},
    {"nombre": "JACQUELINE GUILLEN", "rol": "Analista", "grupo": "TODOS", "pass": "SVCENTRO"}
]

# GESTIÓN DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>BOCADELI - SV CENTRO</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #64748b;'>Control de Acceso Comercial</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nombres = ["-- Seleccione su Nombre --"] + sorted([u["nombre"] for u in USUARIOS_ROLES])
        user_sel = st.selectbox("Usuario", nombres)
        pass_sel = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar al Dashboard", use_container_width=True):
            user_obj = next((u for u in USUARIOS_ROLES if u["nombre"] == user_sel), None)
            if user_obj and pass_sel.strip().lower() == user_obj["pass"].lower():
                st.session_state.autenticado = True
                st.session_state.usuario = user_obj
                st.rerun()
            else:
                st.error("⚠️ Contraseña incorrecta o usuario no seleccionado.")
    st.stop()

# INTERFAZ PRINCIPAL TRAS INICIAR SESIÓN
user = st.session_state.usuario
st.sidebar.markdown(f"👤 **{user['nombre']}** \n*Rol: {user['rol']}*")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.rerun()

st.sidebar.divider()

# PANEL DE ADMINISTRADOR EXCLUSIVO PARA ISRAEL CONSUEGRA
if user["rol"] == "Administrador":
    st.sidebar.subheader("⚙️ Panel de Administración")
    up_csv = st.sidebar.file_uploader("Actualizar Clientes (CSV)", type=["csv"])
    if up_csv:
        with open(csv_path, "wb") as f:
            f.write(up_csv.getbuffer())
        st.sidebar.success("✅ CSV actualizado para todos los usuarios.")
        st.rerun()

    up_json = st.sidebar.file_uploader("Actualizar Geocercas (GeoJSON)", type=["geojson", "json"])
    if up_json:
        with open(geojson_path, "wb") as f:
            f.write(up_json.getbuffer())
        st.sidebar.success("✅ GeoJSON actualizado para todos los usuarios.")
        st.rerun()
    st.sidebar.divider()

# VERIFICACIÓN DE ARCHIVOS
if not os.path.exists(csv_path):
    st.warning("⚠️ No se encuentra el archivo CSV base en el servidor. Por favor, súbelo utilizando el rol de Administrador en el menú lateral.")
    st.stop()

# CARGA DE DATOS DESDE EL SERVIDOR
df = pd.read_csv(csv_path, dtype=str)
df.columns = df.columns.str.strip().str.lower()

# FILTROS EN BARRA LATERAL
st.sidebar.subheader("🔍 Filtros Operativos")
grupo_options = [user["grupo"]] if user["rol"] == "Supervisor" else ["TODOS"] + sorted(df['grupo_clean'].dropna().unique().tolist()) if 'grupo_clean' in df.columns else ["TODOS"]
grupo_sel = st.sidebar.selectbox("Grupo Operativo", grupo_options, disabled=(user["rol"] == "Supervisor"))

rutas_disponibles = ["TODOS"] + sorted(df['ruta_clean'].dropna().unique().tolist()) if 'ruta_clean' in df.columns else ["TODOS"]
ruta_sel = st.sidebar.selectbox("Ruta", rutas_disponibles)

dias_disponibles = ["TODOS", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
dia_sel = st.sidebar.selectbox("Día de Visita", dias_disponibles)

st.title("📊 Dashboard Inteligencia Comercial - Bocadeli SV Centro")
st.write(f"Visualización centralizada en la nube para: **{user['nombre']}**")

# FILTRADO DE DATOS EN PANDAS
df_filtrado = df.copy()
if grupo_sel != "TODOS":
    df_filtrado = df_filtrado[df_filtrado['grupo_clean'] == grupo_sel]
if ruta_sel != "TODOS":
    df_filtrado = df_filtrado[df_filtrado['ruta_clean'] == ruta_sel]
if dia_sel != "TODOS":
    df_filtrado = df_filtrado[df_filtrado['dia_clean'].str.lower() == dia_sel.lower()]

# MÉTRICAS / KPIS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Clientes Filtrados", len(df_filtrado))
col2.metric("Rutas Activas", df_filtrado['ruta_clean'].nunique() if 'ruta_clean' in df_filtrado.columns else 0)
col3.metric("Grupos Activos", df_filtrado['grupo_clean'].nunique() if 'grupo_clean' in df_filtrado.columns else 0)

# MAPA INTERACTIVO CON FOLIUM
st.subheader("🗺️ Mapa de Operación y Cobertura")
m = folium.Map(location=[13.6929, -89.2182], zoom_start=11)

# Pintar puntos en el mapa si existen coordenadas
for _, row in df_filtrado.iterrows():
    try:
        lat = float(row.get('latitud', row.get('lat', 0)))
        lng = float(row.get('longitud', row.get('lng', 0)))
        if lat != 0 and lng != 0:
            nombre_cli = row.get('nombre', 'Cliente')
            codigo_cli = row.get('codigo', 'S/C')
            folium.CircleMarker(
                location=[lat, lng],
                radius=5,
                color="#1e40af",
                fill=True,
                fill_color="#2563eb",
                fill_opacity=0.8,
                popup=f"<b>{nombre_cli}</b><br>Código: {codigo_cli}"
            ).add_to(m)
    except:
        pass

st_folium(m, width="100%", height=450)

# TABLA DETALLE DE CLIENTES
st.subheader("📋 Detalle de Clientes Registrados")
st.dataframe(df_filtrado[['codigo', 'nombre', 'grupo_clean', 'ruta_clean', 'dia_clean', 'direccion']] if not df_filtrado.empty else df_filtrado, use_container_width=True)