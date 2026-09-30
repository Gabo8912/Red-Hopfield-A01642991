
#funcion para aplanar la matriz de pesos
def aplanar_matriz_y_conversion(matriz):
    matriz_aplanada = []
    for j in range(len(matriz)):
        for i in range (len(matriz[j])):
            if matriz[j][i]== 0:
                matriz_aplanada.append(-1)
            else:
                matriz_aplanada.append(matriz[j][i])

    return matriz_aplanada

#funcion para calcular la matriz transpuesta
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
    for i in range(len(resultado)):
        if resultado[i]!=entrada[i]:
            return False
    return True


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
    X1t = matriz_transpuesta(X1, X1)
    X2t = matriz_transpuesta(X2, X2)
    pesos = suma_transpuesta_y_diagonal(X1t, X2t)

    # Entrada con ruido (x1 con un valor cambiado), pasa por el mismo aplanado
    ruidosa = [[-1,-1 ], [-1,-1]]
    ruidosa_a = [
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
]
    actual = aplanar_matriz_y_conversion(ruidosa_a)

    # Recuperación
    estable = False
    tope = 20
    while not estable and tope > 0:
        producto = multiplicar_pesos_por_entrada_ruidosa(pesos, actual)
        nuevo = funcion_de_activacion(producto, actual)
        estable = es_estable(nuevo, actual)   # primero comparo
        actual = nuevo                        # luego actualizo
        tope -= 1

    print("Pesos:", pesos)
    print("Resultado:", actual)
    print("Estable:", estable)
    print("Es X1:", actual == X1)
    print("Es X2:", actual == X2)


if __name__ == "__main__":
    main()