# Ficha del dataset: ocupados GEIH 2025

## Resumen

Datos de personas ocupadas en Colombia durante 2025, usados para estimar la probabilidad de cotizar a pensión.

| Dato | Valor |
|---|---|
| Fuente | Gran Encuesta Integrada de Hogares (GEIH) 2025, DANE |
| Periodo | Enero a diciembre de 2025 (12 meses) |
| Unidad de análisis | Persona ocupada |
| Filas del archivo crudo | 358.029 |
| Filas del archivo limpio | 351.721 |
| Columnas | 26 en cada archivo |
| Variable objetivo | `cotiza_pension` (1 = cotiza, 0 = no cotiza) |

## Origen

Los microdatos provienen del [Archivo Nacional de Datos del DANE](https://microdatos.dane.gov.co). Se descargan con la librería [`dane-data`](https://github.com/IntegralIndefinida/DANE-data) 0.4.0, como muestra `notebooks/generacion_dataset_DANE_geih.ipynb`.

Los datos no se versionan en git. Se esperan en estas rutas:

- `data/raw/geih_2025_ocupados_crudo.csv`
- `data/processed/geih_2025_ocupados_limpio.csv`

`make data` usa el archivo crudo si ya existe; si no, lo descarga. Después genera el archivo limpio.

## Licencia y cita

No se encontró una licencia formal para estos microdatos en las páginas consultadas del DANE, ni permiso expreso de redistribución. El DANE invita a citarlo como fuente e indica que no responde por los cálculos de los usuarios.

Cita sugerida por `dane-data`:

> DANE. Gran Encuesta Integrada de Hogares (GEIH) [microdatos]. Archivo Nacional de Datos (ANDA). https://microdatos.dane.gov.co

La licencia MIT de `dane-data` cubre esa librería, no los datos.

**Pendiente:** confirmar las condiciones de uso en la entrada de la GEIH 2025 o con el DANE.

## Filtros aplicados

| Paso | Regla | Filas excluidas | Filas restantes |
|---|---|---|---|
| 1 | Solo personas ocupadas (`OCI = 1`) | No registrado | 358.029 |
| 2 | Excluir pensionados (`P6920 = 3`) | 6.308 | 351.721 |

La variable objetivo queda con 150.925 personas que cotizan (42,9 %) y 200.796 que no (57,1 %).

La limpieza también elimina `MES` y `OCI`, renombra las columnas, convierte códigos en texto y agrega `ingreso_smmlv` y `gana_1_smmlv_o_mas`. Usa un SMMLV 2025 de $1.423.500.

## Partición

| Conjunto | Meses | Filas |
|---|---|---|
| Entrenamiento | Enero a septiembre | 261.988 |
| Prueba | Octubre a diciembre | 89.733 |

## Columnas

| Columna | Código DANE | Descripción | Uso en el modelo |
|---|---|---|---|
| `anio` | `anio` | Año de la encuesta | No (constante) |
| `mes` | `mes` | Mes de la encuesta | Solo para la partición |
| `directorio` | `DIRECTORIO` | Identificador de la vivienda | No |
| `secuencia_p` | `SECUENCIA_P` | Identificador de la secuencia | No |
| `orden` | `ORDEN` | Número de la persona en el hogar | No |
| `hogar` | `HOGAR` | Número del hogar en la vivienda | No |
| `departamento` | `DPTO` | Departamento | Sí |
| `zona` | `CLASE` | Urbano o rural | Sí |
| `factor_expansion` | `FEX_C18` | Factor de expansión | No |
| `edad` | `P6040` | Edad en años | Sí |
| `sexo` | `P3271` | Sexo | Sí |
| `parentesco_jefe` | `P6050` | Parentesco con el jefe(a) del hogar | Sí |
| `estado_civil` | `P6070` | Estado civil | Sí |
| `nivel_educativo` | `P3042` | Nivel educativo más alto alcanzado | Sí |
| `cotiza_pension` | `P6920` | Cotiza a un fondo de pensiones | Objetivo |
| `posicion_ocupacional` | `P6430` | Posición ocupacional | Sí |
| `tamano_empresa` | `P3069` | Personas en la empresa o negocio | Sí |
| `lugar_trabajo` | `P6880` | Lugar de trabajo (código) | Sí |
| `horas_semana` | `P6800` | Horas trabajadas a la semana | Sí |
| `meses_en_empresa` | `P6426` | Meses en la empresa o negocio | Sí |
| `tiene_contrato` | `P6440` | Contrato (1 = sí, 0 = no) | No (no mejoró ningún modelo) |
| `ingreso` | `INGLABO` | Ingreso laboral mensual en pesos | No (se usa `ingreso_smmlv`) |
| `rama_2d` | `RAMA2D_R4` | Rama de actividad (CIIU Rev. 4, 2 dígitos) | Sí |
| `estrato` | `P4030S1A1` | Estrato de la vivienda | Sí |
| `ingreso_smmlv` | Calculada | Ingreso dividido por el SMMLV 2025 | Sí |
| `gana_1_smmlv_o_mas` | Calculada | 1 si el ingreso es de 1 SMMLV o más | No (solo análisis) |

## Calidad y limitaciones

- **Nulos:** `ingreso` tiene 7.916 (2,25 %), de los cuales 5.660 son familiares sin remuneración. `estrato` tiene 0,43 %.
- **`tiene_contrato`:** vale 1 para todos los asalariados desde el archivo crudo, así que casi equivale a "es asalariado". Falta confirmar a quién se le hace la pregunta.
- **Diccionario:** el archivo crudo solo trae códigos. Las descripciones no salen de un diccionario incluido en el proyecto, y algunos códigos se dedujeron de los datos. El detalle está en las secciones 3 y 9 del EDA.
- **Muestra y población:** los porcentajes sin ponderar describen la muestra. Para estimar la población se usa `factor_expansion`.
- **`horas_semana`:** la mediana baja de 46 a 44 horas desde agosto de 2025, lo que coincide con la reducción de la jornada legal.
