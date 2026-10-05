# NOTA: este archivo es la VISTA del patrón MVC. Solo hace tres cosas:
#   1) mostrar el menú, 2) pedir datos con input(), 3) mostrar resultados con print().
# NO valida reglas del negocio ni abre el archivo JSON: eso lo hace el
# Controlador (views.py). Cada opcion_xxx() pide datos, llama a una función
# del Controlador y muestra lo que esta devuelve.

# Tupla con los nombres de los campos del estudiante (viene del Modelo).
from models import CAMPOS_ESTUDIANTE
# Funciones de apoyo para imprimir con colores y pedir confirmación.
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
# Funciones del Controlador. La Vista las llama pero no sabe cómo funcionan.
from views import (
    crear_estudiante, obtener_todos, obtener_por_id, buscar_estudiantes,
    actualizar_estudiante, eliminar_estudiante, agregar_nota, inscribir_materia,
    obtener_promedio, materias_ofertadas, estudiantes_en_comun
)


# Detiene el programa hasta que el usuario pulse Enter (para poder leer el mensaje).
def pausa():
    input("\nPresione Enter para continuar...")


# Pide un id y lo convierte a entero. Devuelve None si el usuario no escribió
# un número. int("abc") lanza ValueError, que se captura aquí.
def pedir_id(texto="Id del estudiante: "):
    try:
        return int(input(texto))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return None


# Muestra en verde o en rojo la TUPLA (exito, mensaje) que devuelve el Controlador.
def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


# Imprime una tabla con una lista de objetos Estudiante.
def mostrar_tabla(estudiantes):
    # Los números tras ':<' son el ancho de cada columna (alineado a la izquierda).
    print(f"{'ID':<5}{'CARNET':<14}{'NOMBRE':<26}{'EMAIL':<28}{'PROMEDIO':<8}")
    print("-" * 81)
    for e in estudiantes:
        print(f"{e.id:<5}{e.carnet:<14}{e.obtener_nombre_completo():<26}"
              f"{e.email:<28}{e.obtener_promedio():<8}")
    print("-" * 81)
    imprimir_info(f"Total: {len(estudiantes)} estudiante(s)")


# CREAR
def opcion_crear():
    imprimir_titulo("CREAR NUEVO ESTUDIANTE")
    # Recorro la TUPLA de campos del Modelo: si mañana se agrega un campo,
    # este formulario se actualiza solo.
    # Armo un DICCIONARIO {campo: lo que escribió el usuario}.
    datos = {}
    for campo in CAMPOS_ESTUDIANTE:
        datos[campo] = input(f"{campo.capitalize()}: ")
    # crear_estudiante devuelve una TUPLA (exito, mensaje). El * la
    # "desempaqueta" y la pasa como dos argumentos a mostrar_resultado.
    mostrar_resultado(*crear_estudiante(datos))
    pausa()


#  LEER TODOS
def opcion_ver_todos():
    imprimir_titulo("LISTA DE ESTUDIANTES")
    estudiantes = obtener_todos()
    # Una lista vacía es False: 'not estudiantes' significa "no hay ninguno".
    if not estudiantes:
        imprimir_info("Todavía no hay estudiantes. Use la opción 1 para crear el primero.")
    else:
        mostrar_tabla(estudiantes)
    pausa()


# BUSCAR 
def opcion_buscar():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email o carnet: ")
    encontrados = buscar_estudiantes(termino)
    if not encontrados:
        imprimir_info(f"Ningún estudiante coincide con '{termino}'.")
    else:
        mostrar_tabla(encontrados)
    pausa()


#  LEER UNO 
def opcion_ver_por_id():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    id_estudiante = pedir_id()
    # 'is None' porque pedir_id devuelve None cuando el id no era un número.
    if id_estudiante is None:
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
    else:
        # Recorro el DICCIONARIO del estudiante: clave y valor a la vez.
        for clave, valor in estudiante.a_diccionario().items():
            print(f"  {clave.capitalize():<10}: {valor}")
    pausa()


# ACTUALIZAR
def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()

    imprimir_info(f"Editando a {estudiante.obtener_nombre_completo()}")
    print("Deje en blanco el campo que no quiera cambiar.\n")

    # Armo un DICCIONARIO solo con lo que el usuario escribió.
    cambios = {}
    for campo in CAMPOS_ESTUDIANTE:
        # getattr(objeto, "nombre") equivale a objeto.nombre, pero con el
        # nombre del atributo guardado en una variable.
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:                       # un texto vacío es False: se ignora
            cambios[campo] = nuevo

    mostrar_resultado(*actualizar_estudiante(id_estudiante, cambios))
    pausa()


# ELIMINAR
def opcion_eliminar():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()

    imprimir_info(f"Se eliminará: {estudiante}")
    # confirmar() devuelve True solo si respondió "si", "s", "yes" o "y".
    if confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(*eliminar_estudiante(id_estudiante))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# NOTAS
def opcion_agregar_nota():
    imprimir_titulo("AGREGAR NOTA")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    materia = input("Materia: ")
    # La nota se pasa como texto: el Controlador la convierte y valida (0 a 20).
    nota = input("Nota (0 a 20): ")
    mostrar_resultado(*agregar_nota(id_estudiante, materia, nota))
    pausa()


def opcion_inscribir_materia():
    imprimir_titulo("INSCRIBIR EN MATERIA")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()
    materia = input("Materia: ")
    mostrar_resultado(*inscribir_materia(id_estudiante, materia))
    pausa()


def opcion_ver_promedio():
    imprimir_titulo("PROMEDIO DE UN ESTUDIANTE")
    id_estudiante = pedir_id()
    if id_estudiante is None:
        return pausa()

    # DESEMPAQUETADO de la tupla: si exito es False, 'resultado' es un mensaje;
    # si es True, 'resultado' es un DICCIONARIO con el resumen.
    exito, resultado = obtener_promedio(id_estudiante)
    if not exito:
        imprimir_error(resultado)
    else:
        print(f"  Estudiante : {resultado['nombre']}")
        print(f"  Promedio   : {resultado['promedio']}\n")
        if not resultado["por_materia"]:
            imprimir_info("Todavía no tiene notas registradas.")
        # Recorro el diccionario {materia: promedio}.
        for materia, promedio in resultado["por_materia"].items():
            print(f"    {materia:<20} {promedio}")
    pausa()


# CONJUNTOS 
def opcion_materias_en_comun():
    imprimir_titulo("MATERIAS EN COMÚN")
    id_a = pedir_id("Id del primer estudiante: ")
    if id_a is None:
        return pausa()
    id_b = pedir_id("Id del segundo estudiante: ")
    if id_b is None:
        return pausa()

    exito, resultado = estudiantes_en_comun(id_a, id_b)
    if not exito:
        imprimir_error(resultado)
    elif not resultado:                 # un conjunto vacío es False
        imprimir_info("No comparten ninguna materia.")
    else:
        # sorted() convierte el conjunto en lista ordenada (un set no tiene orden).
        imprimir_exito("Materias en común: " + ", ".join(sorted(resultado)))
    pausa()


def opcion_materias_ofertadas():
    imprimir_titulo("MATERIAS OFERTADAS")
    materias = materias_ofertadas()     # CONJUNTO sin repetidos
    if not materias:
        imprimir_info("Todavía no hay materias inscritas.")
    else:
        for materia in sorted(materias):
            print(f"  - {materia}")
        imprimir_info(f"Total: {len(materias)} materia(s)")
    pausa()


# Muestra la despedida y devuelve "salir": main() usa ese valor para cortar el ciclo.
def salir():
    imprimir_info("¡Hasta luego! 👋")
    return "salir"


# DICCIONARIO de opciones: tecla -> (texto del menú, función a ejecutar).
# Reemplaza a un if/elif largo: agregar una opción es agregar una línea,
# y el menú se imprime solo a partir de este mismo diccionario.
OPCIONES = {
    "1": ("Crear estudiante", opcion_crear),
    "2": ("Ver todos", opcion_ver_todos),
    "3": ("Buscar", opcion_buscar),
    "4": ("Ver por id", opcion_ver_por_id),
    "5": ("Actualizar", opcion_actualizar),
    "6": ("Eliminar", opcion_eliminar),
    "7": ("Agregar nota", opcion_agregar_nota),
    "8": ("Ver promedio", opcion_ver_promedio),
    "9": ("Materias en común", opcion_materias_en_comun),
    "10": ("Inscribir en materia", opcion_inscribir_materia),
    "11": ("Materias ofertadas", opcion_materias_ofertadas),
    "0": ("Salir", salir),
}


# Imprime el menú recorriendo el diccionario OPCIONES.
def mostrar_menu():
    imprimir_titulo("SISTEMA DE GESTIÓN DE ESTUDIANTES")
    # .items() da pares (tecla, valor); el valor es una TUPLA (texto, función),
    # que se desempaqueta directamente en el for. '_funcion' no se usa aquí.
    for tecla, (texto, _funcion) in OPCIONES.items():
        print(f"  {tecla:>2}. {texto}")
    print()


# Ciclo principal: muestra el menú, lee la tecla y ejecuta la función elegida.
def main():
    while True:
        mostrar_menu()
        tecla = input("Seleccione una opción: ").strip()
        # 'in' sobre un diccionario busca en las CLAVES (instantáneo).
        if tecla not in OPCIONES:
            imprimir_error("Opción no válida")
            pausa()
            continue                    # vuelve al inicio del while
        _texto, funcion = OPCIONES[tecla]
        # funcion() ejecuta la opción. Solo salir() devuelve "salir".
        if funcion() == "salir":
            break


# Este bloque solo corre al ejecutar "python main.py", no al importarlo.
if __name__ == "__main__":
    try:
        main()
    # Ctrl+C lanza KeyboardInterrupt: se captura para salir sin mostrar errores.
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
