
# Funcion para aplanar un patron y convertir 0 a -1.
def aplanar_matriz_y_conversion(matriz):
    if not isinstance(matriz, (list, tuple)) or not matriz:
        raise ValueError("La matriz debe contener al menos una fila.")
    if not isinstance(matriz[0], (list, tuple)) or not matriz[0]:
        raise ValueError("Las filas deben contener al menos un pixel.")
    columnas = len(matriz[0])
    matriz_aplanada = []
    for j in range(len(matriz)):
        if not isinstance(matriz[j], (list, tuple)) or len(matriz[j]) != columnas:
            raise ValueError("Todas las filas deben tener el mismo tamano.")
        for i in range (len(matriz[j])):
            if type(matriz[j][i]) is not int or matriz[j][i] not in (-1, 0, 1):
                raise ValueError("Los pixeles deben ser enteros: -1, 0 o 1.")
            if matriz[j][i]== 0:
                matriz_aplanada.append(-1)
            else:
                matriz_aplanada.append(matriz[j][i])

    return matriz_aplanada

# Producto externo de dos vectores: aporta los pesos de un patron.
def matriz_transpuesta(m1,m2 ):
    transpuesta=[]
    for j in range(len(m1)):
        fila=[]
        for i in range (len(m2)):
            fila.append(m1[j]*m2[i])
        transpuesta.append(fila)
    return transpuesta

#funcion para sumar la matriz transpuesta y la diagonal OBTENER PESOS
def suma_transpuesta_y_diagonal(m1,m2):
    suma=[]
    for j in range(len(m1)):
        fila=[]
        for i in range(len(m2)):
            if j==i:
                fila.append(0)
            else:
                fila.append(m1[j][i]+m2[j][i])
        suma.append(fila)
    return suma


#funcion para multiplicar pesos por la entrada ruidosa
def multiplicar_pesos_por_entrada_ruidosa(pesos,entrada):
    resultado=[]
    for j in range(len(pesos)):
        suma=0
        for i in range(len(entrada)):
            suma+= entrada[i]*pesos[j][i]
        resultado.append(suma)
    return resultado

#funcion para aplicar funcion de activacion
def funcion_de_activacion(valores, anterior):
    nuevo = []
    for k in range(len(valores)):
        if valores[k] > 0:
            nuevo.append(1)
        elif valores[k] < 0:
            nuevo.append(-1)
        else:
            nuevo.append(anterior[k])
    return nuevo


#funcion para comprobar si es estable
def es_estable(resultado,entrada):
    if len(resultado) != len(entrada):
        return False
    for i in range(len(resultado)):
        if resultado[i]!=entrada[i]:
            return False
    return True


def _validar_vector_bipolar(vector):
    if not isinstance(vector, (list, tuple)) or not vector:
        raise ValueError("El patron debe ser un vector bipolar no vacio.")
    for valor in vector:
        if type(valor) is not int or valor not in (-1, 1):
            raise ValueError("Los vectores deben contener solamente -1 y 1.")


def entrenar_red(patrones):
    """Suma los productos externos de todos los patrones (regla de Hebb)."""
    if not isinstance(patrones, (list, tuple)) or not patrones:
        raise ValueError("Se necesita al menos un patron para entrenar.")
    _validar_vector_bipolar(patrones[0])
    cantidad_neuronas = len(patrones[0])
    pesos = []
    for i in range(cantidad_neuronas):
        pesos.append([0] * cantidad_neuronas)

    for patron in patrones:
        _validar_vector_bipolar(patron)
        if len(patron) != cantidad_neuronas:
            raise ValueError("Todos los patrones deben tener el mismo tamano.")
        for i in range(cantidad_neuronas):
            for j in range(cantidad_neuronas):
                if i != j:
                    pesos[i][j] += patron[i] * patron[j]
    return pesos


def recuperar_patron(pesos, entrada, max_iteraciones=50):
    """Actualiza una neurona a la vez; cada iteracion recorre todo el vector.

    Los pesos deben ser simetricos y tener diagonal cero, como los que devuelve
    entrenar_red. Si la suma es cero, se conserva el valor de la neurona.
    """
    _validar_vector_bipolar(entrada)
    if type(max_iteraciones) is not int or max_iteraciones < 1:
        raise ValueError("El limite de iteraciones debe ser un entero positivo.")
    if not isinstance(pesos, (list, tuple)) or len(pesos) != len(entrada):
        raise ValueError("Los pesos deben coincidir con el tamano de la entrada.")
    for fila in pesos:
        if not isinstance(fila, (list, tuple)) or len(fila) != len(entrada):
            raise ValueError("La matriz de pesos debe ser cuadrada.")
        for peso in fila:
            if type(peso) is not int:
                raise ValueError("Los pesos deben ser enteros, como en entrenar_red.")
    for i in range(len(entrada)):
        if pesos[i][i] != 0:
            raise ValueError("La diagonal de los pesos debe ser cero.")
        for j in range(i):
            if pesos[i][j] != pesos[j][i]:
                raise ValueError("La matriz de pesos debe ser simetrica.")

    actual = list(entrada)
    for iteracion in range(1, max_iteraciones + 1):
        anterior = actual.copy()
        for i in range(len(actual)):
            suma = 0
            for j in range(len(actual)):
                suma += pesos[i][j] * actual[j]
            if suma > 0:
                actual[i] = 1
            elif suma < 0:
                actual[i] = -1
        if es_estable(actual, anterior):
            return {"patron": actual, "estable": True, "iteraciones": iteracion}

    return {"patron": actual, "estable": False, "iteraciones": max_iteraciones}


def main():
    # Patrones guardados
    x1 = [
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
]
    x2 = [
    [1, 0, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0],
    [1, 0, 0, 0, 1],
]
    X1 = aplanar_matriz_y_conversion(x1)
    X2 = aplanar_matriz_y_conversion(x2)

    # Entrenamiento
    pesos = entrenar_red([X1, X2])

    # Entrada con ruido (x1 con un valor cambiado), pasa por el mismo aplanado
    ruidosa_a = [
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
]
    actual = aplanar_matriz_y_conversion(ruidosa_a)

    # Recuperación
    recuperacion = recuperar_patron(pesos, actual, max_iteraciones=20)
    actual = recuperacion["patron"]

    print("Pesos:", pesos)
    print("Resultado:", actual)
    print("Estable:", recuperacion["estable"])
    print("Es X1:", actual == X1)
    print("Es X2:", actual == X2)


if __name__ == "__main__":
    main()
