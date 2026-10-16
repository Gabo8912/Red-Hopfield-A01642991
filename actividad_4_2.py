"""Actividad 4.2: generación de melodías mediante una cadena de Markov.

Ejecutar en Windows:
    python actividad_4_2.py

Simular sin reproducir sonido, en cualquier sistema:
    python actividad_4_2.py --sin-audio

Solo utiliza bibliotecas incluidas con Python.
"""

import argparse
import math
import random
import time


# PASO 1. Definir los estados y calcular sus frecuencias.
NOTAS = ["Do4", "Re4", "Mi4", "Fa4", "Sol4", "La4", "Si4", "Do5"]
NUMEROS_MIDI = [60, 62, 64, 65, 67, 69, 71, 72]

# La4 corresponde al número MIDI 69 y a la frecuencia de 440 Hz.
FRECUENCIAS = [
    round(440 * 2 ** ((numero - 69) / 12))
    for numero in NUMEROS_MIDI
]


# PASO 2. Proponer una matriz de transición estocástica.
# Cada fila representa la nota actual; cada columna, la siguiente.
# El orden de filas y columnas coincide con NOTAS.
#         Do4   Re4   Mi4   Fa4  Sol4   La4   Si4   Do5
P = [
    [0.10, 0.25, 0.25, 0.10, 0.20, 0.05, 0.03, 0.02],  # Do4
    [0.15, 0.10, 0.25, 0.15, 0.20, 0.10, 0.03, 0.02],  # Re4
    [0.20, 0.10, 0.10, 0.25, 0.20, 0.10, 0.03, 0.02],  # Mi4
    [0.10, 0.05, 0.10, 0.10, 0.35, 0.15, 0.05, 0.10],  # Fa4
    [0.25, 0.05, 0.10, 0.10, 0.10, 0.10, 0.10, 0.20],  # Sol4
    [0.10, 0.10, 0.15, 0.10, 0.15, 0.10, 0.20, 0.10],  # La4
    [0.05, 0.03, 0.03, 0.04, 0.10, 0.10, 0.10, 0.55],  # Si4
    [0.10, 0.05, 0.10, 0.05, 0.20, 0.15, 0.25, 0.10],  # Do5
]


def validar_matriz():
    """Comprueba las dimensiones y que cada fila sea una distribución válida."""
    cantidad_estados = len(NOTAS)
    if len(P) != cantidad_estados:
        raise ValueError("Debe existir una fila por nota.")

    for indice, fila in enumerate(P):
        if len(fila) != cantidad_estados:
            raise ValueError(
                f"La fila {indice} debe tener {cantidad_estados} columnas."
            )
        for probabilidad in fila:
            if (
                type(probabilidad) not in (int, float)
                or not math.isfinite(probabilidad)
                or not 0 <= probabilidad <= 1
            ):
                raise ValueError(
                    f"La fila {indice} contiene una probabilidad inválida."
                )

        # Los decimales pueden tener pequeños errores de punto flotante.
        if not math.isclose(sum(fila), 1.0, rel_tol=0, abs_tol=1e-9):
            raise ValueError(f"La fila {indice} no suma 1.")


# PASO 3. Elegir cada nota utilizando la fila del estado actual.
def generar_melodia(n_notas=32, inicio="Do4", semilla=None):
    """Devuelve una lista de índices: n notas implican n - 1 transiciones."""
    validar_matriz()
    if type(n_notas) is not int or n_notas < 1:
        raise ValueError("La cantidad de notas debe ser un entero positivo.")
    if inicio not in NOTAS:
        raise ValueError("La nota inicial no pertenece al modelo.")


    azar = random.Random(semilla)
    actual = NOTAS.index(inicio)
    melodia = [actual]

    for _ in range(n_notas - 1):
        actual = azar.choices(
            range(len(NOTAS)),
            weights=P[actual],
            k=1,
        )[0]
        melodia.append(actual)

    return melodia


# PASO 4. Imprimir cada nota inmediatamente antes de reproducirla.
def reproducir_melodia(melodia, duracion_ms=350, pausa_ms=50, audio=True):
    """Reproduce tonos en Windows o imprime una simulación sin sonido."""
    if type(duracion_ms) is not int or duracion_ms <= 0:
        raise ValueError("La duración debe ser un entero positivo en milisegundos.")
    if type(pausa_ms) is not int or pausa_ms < 0:
        raise ValueError("La pausa debe ser un entero no negativo en milisegundos.")
    if not isinstance(melodia, (list, tuple)) or not melodia:
        raise ValueError("La melodía debe contener al menos una nota.")
    for estado in melodia:
        if type(estado) is not int or not 0 <= estado < len(NOTAS):
            raise ValueError("La melodía contiene un estado inválido.")

    if audio:
        try:
            import winsound
        except ImportError as error:
            raise RuntimeError(
                "La reproducción requiere Windows. Usa --sin-audio para simular."
            ) from error

    for posicion, estado in enumerate(melodia, start=1):
        frecuencia = FRECUENCIAS[estado]
        accion = "Sonando" if audio else "Simulación"
        print(
            f"{posicion:02d}. {accion}: {NOTAS[estado]} | "
            f"{frecuencia} Hz | {duracion_ms} ms",
            flush=True,
        )

        if audio:
            winsound.Beep(frecuencia, duracion_ms)
            time.sleep(pausa_ms / 1000)


# PASO 5. Configurar y ejecutar el experimento desde la terminal.
def main():
    parser = argparse.ArgumentParser(
        description="Genera melodías con una cadena de Markov de primer orden."
    )
    parser.add_argument("--notas", type=int, default=32, help="cantidad de notas")
    parser.add_argument(
        "--inicio", choices=NOTAS, default="Do4", help="nota inicial"
    )
    parser.add_argument(
        "--semilla", type=int, default=42, help="semilla del generador aleatorio"
    )
    parser.add_argument(
        "--duracion", type=int, default=350, help="duración de cada tono en ms"
    )
    parser.add_argument(
        "--pausa", type=int, default=50, help="pausa después de cada tono en ms"
    )
    parser.add_argument(
        "--sin-audio", action="store_true", help="simular sin emitir sonido"
    )
    args = parser.parse_args()

    try:
        melodia = generar_melodia(args.notas, args.inicio, args.semilla)
        print(
            f"Melodía de {len(melodia)} notas y "
            f"{len(melodia) - 1} transiciones.\n"
        )
        reproducir_melodia(
            melodia,
            duracion_ms=args.duracion,
            pausa_ms=args.pausa,
            audio=not args.sin_audio,
        )
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
