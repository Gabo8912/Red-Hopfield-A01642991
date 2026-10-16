import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from redHopfield import aplanar_matriz_y_conversion, entrenar_red, recuperar_patron
from reconocerFiguras import PATRONES_FIGURAS, agregar_ruido, reconocer_figura


RAIZ = Path(__file__).resolve().parents[1]


class RedHopfieldTests(unittest.TestCase):
    def test_conversion_binaria_y_bipolar(self):
        self.assertEqual(aplanar_matriz_y_conversion([[0, 1], [-1, 0]]), [-1, 1, -1, -1])

    def test_matrices_invalidas(self):
        for matriz in ([], [[]], [[0], [1, 0]], [[2]], [[True]], [[0.0]], [1], None):
            with self.subTest(matriz=matriz), self.assertRaises(ValueError):
                aplanar_matriz_y_conversion(matriz)

    def test_entrenamiento_con_tres_patrones(self):
        pesos = entrenar_red([[1, 1, 1], [1, -1, 1], [-1, 1, 1]])
        self.assertEqual(pesos, [[0, -1, 1], [-1, 0, 1], [1, 1, 0]])

    def test_patrones_invalidos_para_entrenar(self):
        for patrones in ([], [[1, -1], [1]], [[1, 0]], [[]], None):
            with self.subTest(patrones=patrones), self.assertRaises(ValueError):
                entrenar_red(patrones)

    def test_actualizacion_secuencial_resuelve_un_ciclo_sincrono(self):
        # La actualizacion simultanea alternaria [1, -1] y [-1, 1].
        entrada = [1, -1]
        resultado = recuperar_patron([[0, 1], [1, 0]], entrada)
        self.assertEqual(resultado, {"patron": [-1, -1], "estable": True, "iteraciones": 2})
        self.assertEqual(entrada, [1, -1])

    def test_activacion_cero_conserva_el_estado(self):
        resultado = recuperar_patron([[0, 0], [0, 0]], [1, -1])
        self.assertEqual(resultado, {"patron": [1, -1], "estable": True, "iteraciones": 1})

    def test_pesos_invalidos(self):
        for pesos in ([[0]], [[0, 1]], [[1, 0], [0, 0]], [[0, 1], [2, 0]], [[0, "a"], ["a", 0]]):
            with self.subTest(pesos=pesos), self.assertRaises(ValueError):
                recuperar_patron(pesos, [1, -1])

    def test_limite_de_iteraciones_invalido(self):
        for limite in (0, -1, 1.5, True):
            with self.subTest(limite=limite), self.assertRaises(ValueError):
                recuperar_patron([[0]], [1], limite)


class ReconocimientoFigurasTests(unittest.TestCase):
    def test_las_tres_figuras_son_memorias_estables(self):
        for nombre, matriz in PATRONES_FIGURAS.items():
            original = [fila[:] for fila in matriz]
            with self.subTest(figura=nombre):
                resultado = reconocer_figura(matriz)
                self.assertEqual(resultado["figura"], nombre)
                self.assertEqual(resultado["matriz_recuperada"], matriz)
                self.assertTrue(resultado["estable"])
                self.assertEqual(resultado["iteraciones"], 1)
                self.assertEqual(matriz, original)

    def test_recupera_cualquier_inversion_de_un_pixel(self):
        for nombre, matriz in PATRONES_FIGURAS.items():
            for posicion in range(81):
                entrada = [fila[:] for fila in matriz]
                entrada[posicion // 9][posicion % 9] ^= 1
                with self.subTest(figura=nombre, pixel=posicion):
                    resultado = reconocer_figura(entrada)
                    self.assertEqual(resultado["figura"], nombre)
                    self.assertEqual(resultado["matriz_recuperada"], matriz)

    def test_recupera_ruido_reproducible(self):
        for nombre, matriz in PATRONES_FIGURAS.items():
            for cantidad in (5, 8, 10):
                for semilla in (0, 1, 7, 42, 2026):
                    with self.subTest(figura=nombre, ruido=cantidad, semilla=semilla):
                        resultado = reconocer_figura(agregar_ruido(matriz, cantidad, semilla))
                        self.assertEqual(resultado["figura"], nombre)
                        self.assertEqual(resultado["matriz_recuperada"], matriz)

    def test_ruido_invierte_la_cantidad_exacta_y_no_modifica_el_original(self):
        matriz = PATRONES_FIGURAS["circulo"]
        original = [fila[:] for fila in matriz]
        entrada = agregar_ruido(matriz, 10)
        cambios = sum(a != b for fila_a, fila_b in zip(matriz, entrada) for a, b in zip(fila_a, fila_b))
        self.assertEqual(cambios, 10)
        self.assertEqual(matriz, original)
        self.assertEqual(entrada, agregar_ruido(matriz, 10))
        self.assertEqual(agregar_ruido(matriz, 0), matriz)
        self.assertEqual(agregar_ruido(matriz, 81), [[1 - p for p in fila] for fila in matriz])
        for cantidad in (-1, 82, 0.5, True):
            with self.subTest(cantidad=cantidad), self.assertRaises(ValueError):
                agregar_ruido(matriz, cantidad)

    def test_estado_espurio_no_recibe_etiqueta(self):
        # Las memorias invertidas tambien son atractores, pero no figuras guardadas.
        invertida = [[1 - pixel for pixel in fila] for fila in PATRONES_FIGURAS["triangulo"]]
        resultado = reconocer_figura(invertida)
        self.assertTrue(resultado["estable"])
        self.assertIsNone(resultado["figura"])

    def test_no_etiqueta_un_estado_sin_estabilidad_confirmada(self):
        entrada = agregar_ruido(PATRONES_FIGURAS["triangulo"], 8)
        resultado = reconocer_figura(entrada, max_iteraciones=1)
        self.assertFalse(resultado["estable"])
        self.assertEqual(resultado["iteraciones"], 1)
        self.assertIsNone(resultado["figura"])

    def test_solo_acepta_0_y_1_y_dimensiones_correctas(self):
        for entrada in ([[0] * 9] * 8, [[0] * 27] * 3, [[-1] * 9] * 9):
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                reconocer_figura(entrada)

    def test_permite_entrenar_figuras_personalizadas(self):
        patron = [[1, 0], [0, 1]]
        resultado = reconocer_figura(patron, patrones={"diagonal": patron})
        self.assertEqual(resultado["figura"], "diagonal")
        self.assertEqual(resultado["matriz_recuperada"], patron)

    def test_rechaza_un_catalogo_vacio_o_ambiguo(self):
        patron = PATRONES_FIGURAS["cuadrado"]
        for patrones in ({}, {"": patron}, {"a": patron, "b": patron}):
            with self.subTest(patrones=patrones), self.assertRaises(ValueError):
                reconocer_figura(patron, patrones=patrones)


class ConsolaTests(unittest.TestCase):
    def ejecutar(self, archivo, *argumentos):
        return subprocess.run(
            [sys.executable, "-B", str(RAIZ / archivo), *argumentos],
            cwd=RAIZ, capture_output=True, text=True, check=False,
        )

    def test_ejemplo_json(self):
        resultado = self.ejecutar("reconocerFiguras.py", "--entrada", "ejemplos/triangulo_ruidoso.json")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Figura reconocida: triangulo", resultado.stdout)
        self.assertIn("Estable: True", resultado.stdout)

    def test_entrada_json_invalida_muestra_error_sin_traceback(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "invalida.json"
            ruta.write_text(json.dumps([[2]]), encoding="utf-8")
            resultado = self.ejecutar("reconocerFiguras.py", "--entrada", str(ruta))
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("error:", resultado.stderr)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_ejemplo_original_sigue_recuperando_la_cruz(self):
        resultado = self.ejecutar("redHopfield.py")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Estable: True", resultado.stdout)
        self.assertIn("Es X1: True", resultado.stdout)
        self.assertIn("Es X2: False", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
