"""
for i in range(0, len(lineas)):
    linea = lineas[i].partition("=")
    variable = linea[0].strip()
    contenido = linea[2].strip()
    if variable == 'servidor':
        servidor = contenido
    elif variable == 'canal':
        canal = contenido
    elif variable == 'nick':
        nick = contenido
"""

def configuracion(ivariable):
    archivo = open('configuracion.txt')
    lineas = archivo.readlines()
    for i in range(0, len(lineas)):
        linea = lineas[i].partition("=")
        variable = linea[0].strip()
        contenido = linea[2].strip()
        if ivariable == variable:
            resultado = contenido
            return resultado

#print "El servidor es ",servidor,", el canal es ",canal,"y el nick es ",nick
