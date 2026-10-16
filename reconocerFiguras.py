"""Reconocimiento de figuras con una red de Hopfield hecha con listas y ciclos."""

import argparse
import json
import random
from pathlib import Path

from redHopfield import aplanar_matriz_y_conversion, entrenar_red, recuperar_patron


PATRONES_FIGURAS = {
    "cuadrado": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "circulo": [
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
    ],
    "triangulo": [
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
}


def _validar_matriz_binaria(matriz):
    vector = aplanar_matriz_y_conversion(matriz)
    for fila in matriz:
        for pixel in fila:
            if pixel not in (0, 1):
                raise ValueError("Las figuras deben contener solamente 0 y 1.")
    return vector


def _vector_a_matriz(vector, filas, columnas):
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(1 if vector[i * columnas + j] == 1 else 0)
        matriz.append(fila)
    return matriz


def agregar_ruido(matriz, cantidad, semilla=42):
    """Invierte una cantidad exacta de pixeles sin modificar la matriz original."""
    vector = _validar_matriz_binaria(matriz)
    if type(cantidad) is not int or not 0 <= cantidad <= len(vector):
        raise ValueError(f"El ruido debe ser un entero entre 0 y {len(vector)} pixeles.")
    posiciones = random.Random(semilla).sample(range(len(vector)), cantidad)
    for posicion in posiciones:
        vector[posicion] *= -1
    return _vector_a_matriz(vector, len(matriz), len(matriz[0]))


def reconocer_figura(entrada, patrones=None, max_iteraciones=50):
    """Recupera la entrada y etiqueta solo una memoria exacta y estable.

    Las matrices usan 0 y 1 y deben tener las mismas dimensiones. Los patrones
    por defecto son de 9x9; se pueden pasar otros mediante un diccionario de
    nombres y matrices. Un estado espurio o sin convergencia da figura=None.
    """
    vector_entrada = _validar_matriz_binaria(entrada)
    if patrones is None:
        patrones = PATRONES_FIGURAS
    if not isinstance(patrones, dict) or not patrones:
        raise ValueError("Se necesita un diccionario de figuras para entrenar.")

    vectores = {}
    for nombre, matriz in patrones.items():
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Cada figura debe tener un nombre no vacio.")
        vector = _validar_matriz_binaria(matriz)
        if len(matriz) != len(entrada) or len(matriz[0]) != len(entrada[0]):
            raise ValueError(
                f"La entrada debe tener las mismas dimensiones que '{nombre}' "
                f"({len(matriz)}x{len(matriz[0])})."
            )
        if vector in vectores.values():
            raise ValueError("Dos figuras no pueden tener el mismo patron.")
        vectores[nombre] = vector

    pesos = entrenar_red(list(vectores.values()))
    resultado = recuperar_patron(pesos, vector_entrada, max_iteraciones)
    figura = None
    if resultado["estable"]:
        for nombre, vector in vectores.items():
            if resultado["patron"] == vector:
                figura = nombre
                break
    return {
        "figura": figura,
        "matriz_recuperada": _vector_a_matriz(
            resultado["patron"], len(entrada), len(entrada[0])
        ),
        "estable": resultado["estable"],
        "iteraciones": resultado["iteraciones"],
    }


def imprimir_matriz(matriz):
    for fila in matriz:
        print(" ".join(str(pixel) for pixel in fila))


def main():
    parser = argparse.ArgumentParser(
        description="Reconoce circulo, cuadrado y triangulo con una red de Hopfield."
    )
    fuente = parser.add_mutually_exclusive_group()
    fuente.add_argument(
        "--figura", choices=list(PATRONES_FIGURAS), default="triangulo",
        help="figura para la demostracion (por defecto: triangulo)",
    )
    fuente.add_argument("--entrada", type=Path, help="archivo JSON con una matriz 0/1 de 9x9")
    parser.add_argument(
        "--ruido", type=int,
        help="pixeles a invertir (por defecto: 8 en la demo, 0 con --entrada)",
    )
    parser.add_argument("--semilla", type=int, default=42, help="semilla del ruido aleatorio")
    parser.add_argument("--max-iteraciones", type=int, default=50, help="limite de recorridos")
    args = parser.parse_args()

    try:
        if args.entrada is not None:
            matriz = json.loads(args.entrada.read_text(encoding="utf-8-sig"))
            cantidad_ruido = 0 if args.ruido is None else args.ruido
        else:
            matriz = PATRONES_FIGURAS[args.figura]
            cantidad_ruido = 8 if args.ruido is None else args.ruido
        entrada = agregar_ruido(matriz, cantidad_ruido, args.semilla)
        resultado = reconocer_figura(entrada, max_iteraciones=args.max_iteraciones)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

    print("Entrada (1 = figura, 0 = fondo):")
    imprimir_matriz(entrada)
    print("\nFigura recuperada:")
    imprimir_matriz(resultado["matriz_recuperada"])
    print("\nFigura reconocida:", resultado["figura"] or "No reconocida")
    print("Estable:", resultado["estable"])
    print("Iteraciones:", resultado["iteraciones"])
    if not resultado["estable"]:
        print("Se alcanzo el limite de iteraciones sin confirmar estabilidad.")
    elif resultado["figura"] is None:
        print("El estado estable no coincide con una figura almacenada.")


if __name__ == "__main__":
    main()
