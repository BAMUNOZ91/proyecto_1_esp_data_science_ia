"""App de Streamlit: probabilidad de que un trabajador colombiano cotice a pensión.

Ejecutar desde la raíz del proyecto (antes hay que entrenar el modelo con `make train`):

    uv run streamlit run app/app.py
"""

import streamlit as st

from cotiza_pension.formulario import (
    ROTULOS,
    armar_datos,
    etiqueta,
    opciones_categoricas,
)
from cotiza_pension.predict import obtener_pipeline, predecir

st.set_page_config(page_title="¿Cotiza a pensión?", page_icon="📊")
st.title("¿Este trabajador cotiza a pensión?")
st.write(
    "Llena el perfil de una persona ocupada y el modelo estima la probabilidad de que cotice "
    "a pensión. El modelo se entrenó con la GEIH 2025 del DANE (enero a septiembre)."
)

try:
    pipeline = obtener_pipeline()
except FileNotFoundError:
    st.error("No hay un modelo entrenado. Ejecuta primero `make train` y recarga la página.")
    st.stop()

opciones = opciones_categoricas(pipeline)


def elegir(columna: str, contenedor, por_defecto=None):
    """Lista desplegable con las opciones que conoce el modelo para `columna`."""
    valores = opciones[columna]
    indice = valores.index(por_defecto) if por_defecto in valores else 0
    return contenedor.selectbox(
        ROTULOS[columna],
        valores,
        index=indice,
        format_func=lambda v: etiqueta(columna, v),
        key=columna,
    )


with st.form("perfil"):
    st.subheader("Persona")
    c1, c2 = st.columns(2)
    edad = c1.number_input(ROTULOS["edad"], min_value=10, max_value=110, value=35, step=1)
    categoricas = {
        "sexo": elegir("sexo", c2),
        "estado_civil": elegir("estado_civil", c1),
        "parentesco_jefe": elegir("parentesco_jefe", c2),
        "nivel_educativo": elegir("nivel_educativo", c1, "Media académica"),
    }

    st.subheader("Vivienda")
    c1, c2 = st.columns(2)
    categoricas["departamento"] = elegir("departamento", c1, "Bogotá D.C.")
    categoricas["zona"] = elegir("zona", c2)
    categoricas["estrato"] = elegir("estrato", c1, "2.0")

    st.subheader("Trabajo")
    c1, c2 = st.columns(2)
    categoricas["posicion_ocupacional"] = elegir("posicion_ocupacional", c1)
    categoricas["tamano_empresa"] = elegir("tamano_empresa", c2)
    categoricas["rama_2d"] = elegir("rama_2d", c1, "47.0")
    categoricas["lugar_trabajo"] = elegir("lugar_trabajo", c2)
    horas = c1.number_input(ROTULOS["horas_semana"], min_value=0, max_value=130, value=48, step=1)
    meses = c2.number_input(
        ROTULOS["meses_en_empresa"], min_value=0, max_value=900, value=24, step=1
    )

    st.subheader("Ingreso")
    no_reporta = st.checkbox("No reporta ingreso")
    ingreso = st.number_input(
        ROTULOS["ingreso_smmlv"], min_value=0, value=1_423_500, step=50_000, format="%d"
    )
    enviado = st.form_submit_button("Calcular probabilidad")

if enviado:
    datos = armar_datos(
        {"edad": edad, "horas_semana": float(horas), "meses_en_empresa": float(meses)},
        categoricas,
        None if no_reporta else float(ingreso),
    )
    resultado = predecir(datos)
    probabilidad = resultado["probabilidad_cotizar"]
    st.metric("Probabilidad de cotizar", f"{probabilidad:.0%}")
    st.progress(probabilidad)
    if resultado["cotiza"]:
        st.success("El modelo predice que esta persona **cotiza** a pensión.")
    else:
        st.warning("El modelo predice que esta persona **no cotiza** a pensión.")
    st.caption(
        "Es una estimación con datos de una encuesta, no un dato real de la persona. "
        "El modelo acierta menos con asalariados de microempresas que ganan 1 SMMLV o más."
    )
