# Red-Hopfield-A01642991

Red de Hopfield implementada con listas, condiciones y ciclos para entender su
funcionamiento. La rama `feature/reconocimiento-figuras` agrega reconocimiento de
**cuadrado, círculo y triángulo** mediante matrices de **0 y 1**.

## Análisis de la implementación original

`redHopfield.py` almacena una cruz y una X de 5×5. Convierte los ceros a -1,
calcula los productos externos de los patrones, suma sus pesos y pone la
diagonal en cero. Su función `matriz_transpuesta` calcula un **producto externo**,
aunque el nombre diga transpuesta. La activación conserva el valor anterior
cuando la suma es cero, lo cual evita cambios innecesarios.

El entrenamiento original estaba limitado a dos patrones y la recuperación
actualizaba todas las neuronas a la vez. La nueva versión permite entrenar varios
patrones con `entrenar_red` y recuperarlos con `recuperar_patron`, que actualiza
una neurona a la vez. Un recorrido completo sin cambios confirma la estabilidad;
si se agota el límite, el resultado indica que no se confirmó la convergencia.
El ejemplo original sigue disponible y utiliza estas funciones compartidas.

## Ejecutar el reconocimiento

Se necesita Python 3. No requiere instalar paquetes externos.

```bash
python reconocerFiguras.py
python reconocerFiguras.py --figura circulo --ruido 8
python reconocerFiguras.py --figura cuadrado --ruido 10 --semilla 42
```

La demostración predeterminada usa un triángulo con ocho píxeles invertidos y
semilla 42. `--ruido` especifica una cantidad de píxeles, entre 0 y 81, no un
porcentaje. El programa imprime la entrada, la matriz recuperada, el nombre de
la figura, la estabilidad y el número de recorridos.

### Usar tu propia matriz de 0 y 1

Guarda una lista de nueve filas con nueve enteros por fila en un archivo JSON.
**1** representa la figura y **0** el fondo. Puedes partir del ejemplo incluido:

```bash
python reconocerFiguras.py --entrada ejemplos/triangulo_ruidoso.json
```

Con `--entrada` se procesa la matriz tal como está. Para agregar ruido adicional,
usa `--ruido`. También puedes definir `--max-iteraciones`, cuyo valor
predeterminado es 50. Los tamaños incorrectos, filas desiguales y valores
distintos de 0 y 1 producen un mensaje de error.

### Usarlo desde Python

```python
from reconocerFiguras import PATRONES_FIGURAS, agregar_ruido, reconocer_figura

entrada = agregar_ruido(PATRONES_FIGURAS["triangulo"], cantidad=8, semilla=42)
resultado = reconocer_figura(entrada)
print(resultado["figura"])             # triangulo
print(resultado["matriz_recuperada"])  # matriz de 0 y 1
```

Puedes sustituir `entrada` por tu propia matriz. Para entrenar otras figuras,
agrega matrices a `PATRONES_FIGURAS` o pasa un diccionario mediante
`reconocer_figura(entrada, patrones=mis_figuras)`. Todas las matrices deben tener
las mismas dimensiones y patrones distintos.

## Cómo reconoce las figuras

1. Convierte cada matriz binaria en un vector bipolar: 0 pasa a -1 y 1 queda en 1.
2. Entrena 81 neuronas con la regla de Hebb: suma los productos externos de los
   patrones y deja la diagonal de los pesos en cero.
3. Recupera la entrada con actualizaciones secuenciales hasta que un recorrido
   no cambie ninguna neurona o se alcance el límite de iteraciones.
4. Compara el estado estable con los patrones almacenados y devuelve su nombre
   solamente si coincide exactamente con uno de ellos.

La interfaz de entrada y salida usa 0 y 1; los valores -1 y 1 son internos a la
red. Un estado estable que no corresponda a una memoria, o una recuperación sin
estabilidad confirmada, devuelve `figura=None` y muestra `No reconocida`.

La red recupera patrones cercanos a sus memorias. Las figuras deben conservar
su posición, escala y orientación dentro de la cuadrícula: no reconoce cualquier
dibujo geométrico arbitrario. Con demasiado ruido puede recuperar otra figura o
un estado espurio; incluso una entrada desconocida puede caer en una memoria
conocida. Agregar patrones similares puede reducir la capacidad de recuperación.

## Verificación

```bash
python -m unittest discover -s tests -v
python redHopfield.py
```

Las pruebas verifican los pesos, la recuperación secuencial, las tres figuras
sin ruido y con ruido reproducible, cada posible inversión de un solo píxel,
la validación de entradas, los estados espurios y el límite de iteraciones.
