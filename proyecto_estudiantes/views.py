# NOTA: este archivo NO define una clase. Es un MÓDULO con funciones sueltas que
# hacen el CRUD de estudiantes (Crear, Leer, Actualizar, Eliminar) + búsqueda,
# notas, promedio y materias.
# Aunque se llama "views", en MVC cumple el papel de CONTROLADOR: tiene la lógica
# y las validaciones, pero NO usa print() ni input() en sus funciones. Eso lo
# hace main.py (la Vista).
# Las funciones que modifican datos devuelven una tupla (exito, mensaje).

# 'os' sirve para armar la ruta del archivo JSON sin depender de desde qué
# carpeta se ejecute el programa.
import os

# Importa la clase Estudiante (el Modelo) y la tupla con los nombres de sus campos.
from models import Estudiante, CAMPOS_ESTUDIANTE
# Importa la clase que lee y guarda la lista de registros en el archivo JSON.
from shared.json_manager import GestorJSON
# Importa la función que revisa si un texto tiene formato de correo.
from shared.herramientas import es_email_valido


# __file__ es la ruta de ESTE archivo; abspath la vuelve absoluta y dirname
# se queda con su carpeta. Así "data/" siempre queda junto a views.py.
CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_JSON = os.path.join(CARPETA_PROYECTO, "data", "estudiantes.json")

# Crea UN solo gestor para todo el módulo, apuntando al archivo de estudiantes.
# Al crearse, si la carpeta "data" no existe, GestorJSON la crea.
# Todas las funciones de abajo usan esta misma variable global 'gestor'.
gestor = GestorJSON(RUTA_JSON)

# TUPLAS de configuración: fijas, nadie las modifica en tiempo de ejecución
# Campos que el usuario DEBE llenar para poder crear un estudiante.
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
# Campos en los que se busca al usar buscar_estudiantes().
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")
# Rango válido de una nota: (mínimo, máximo). Es tupla porque es un par fijo.
RANGO_NOTA = (0, 20)


# ===================== AYUDAS INTERNAS =====================

# Devuelve un CONJUNTO con todos los emails guardados (en minúsculas).
# 'excepto_id' es opcional: sirve para ignorar el email de un estudiante concreto
# (se usa al actualizar, para que no choque con su propio email).
def emails_registrados(excepto_id=None):
    """CONJUNTO con los emails ya usados. Sirve para detectar duplicados al instante."""
    # COMPRENSIÓN DE CONJUNTO: { expresión for ... if ... }
    # "Para cada registro del archivo, si su id no es excepto_id, agrega su
    # email en minúsculas al conjunto."
    return {
        registro["email"].lower()           # .lower(): "Ana@X.com" y "ana@x.com" son iguales
        for registro in gestor.leer()       # recorre la lista de diccionarios del JSON
        if registro["id"] != excepto_id     # filtro: salta al estudiante que se edita
    }
    # Se usa un conjunto porque 'in' en un set es casi instantáneo (usa hash),
    # mientras que en una lista hay que revisar elemento por elemento.


# Igual que la anterior pero con los CARNETS (en mayúsculas).
# Es el segundo conjunto que exige la tarea: el carnet no se puede repetir.
def carnets_registrados(excepto_id=None):
    """CONJUNTO con los carnets ya usados."""
    return {
        registro["carnet"].upper()          # .upper(): "est1" y "EST1" son el mismo carnet
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


# Calcula el id que le toca al próximo estudiante.
def siguiente_id():
    # COMPRENSIÓN DE LISTA: saca solo el "id" de cada registro. Ej: [1, 2, 5]
    ids = [registro["id"] for registro in gestor.leer()]
    # Si hay ids, toma el mayor y le suma 1 (ej: 5 + 1 = 6).
    # Si la lista está vacía (no hay estudiantes), empieza en 1.
    # (Si se elimina el estudiante con el id más alto, ese id se vuelve a usar.)
    return max(ids) + 1 if ids else 1


# Busca en qué POSICIÓN de la lista está el registro con ese id.
# Devuelve el índice, o None si no existe. El '_' inicial indica "uso interno".
def _posicion_por_id(registros, id_estudiante):
    # enumerate me da índice y valor a la vez. Ej: enumerate([a, b]) -> (0, a), (1, b)
    for indice, registro in enumerate(registros):
        if registro["id"] == id_estudiante:
            return indice       # return corta la función y el ciclo de inmediato
    return None                 # el for terminó sin encontrarlo


# CREATE 

# Crea un estudiante nuevo después de validar sus datos, y lo guarda en el archivo.
def crear_estudiante(datos):
    """datos: diccionario con las claves de CAMPOS_ESTUDIANTE. Devuelve (exito, mensaje)."""
    # try/except: si ocurre CUALQUIER error inesperado, el programa no se cae;
    # salta al 'except' del final y devuelve un mensaje de error.
    try:
        # 1) Normalizo: un diccionario con todos los campos, sin espacios sobrantes
        # COMPRENSIÓN DE DICCIONARIO: {clave: valor for ...}
        #   - datos.get(campo, "") -> el valor del campo, o "" si no vino.
        #   - str(...)             -> lo convierte a texto (por si llega un número).
        #   - .strip()             -> quita espacios al inicio y al final.
        valores = {campo: str(datos.get(campo, "")).strip() for campo in CAMPOS_ESTUDIANTE}

        # 2) Reviso obligatorios recorriendo la TUPLA
        # Lista con los campos obligatorios que quedaron vacíos ("" cuenta como False).
        faltantes = [campo for campo in CAMPOS_OBLIGATORIOS if not valores[campo]]
        # Una lista con elementos es True: si falta alguno, se detiene aquí.
        if faltantes:
            # ', '.join(lista) une los elementos con coma. Ej: "nombre, email"
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

        # 3) Formato del email
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"

        # 4) Email duplicado: búsqueda instantánea dentro del CONJUNTO
        # Se compara en minúsculas, igual que como se guardan en el conjunto.
        if valores["email"].lower() in emails_registrados():
            return False, "Ese email ya está registrado"

        # 5) Carnet duplicado: otro CONJUNTO. Se normaliza a mayúsculas ANTES
        # de comparar y de guardar, para que "est1" y "EST1" sean el mismo.
        valores["carnet"] = valores["carnet"].upper()
        if valores["carnet"] in carnets_registrados():
            return False, f"El carnet {valores['carnet']} ya está registrado"

        # 6) Creo el objeto del Modelo, pasando cada campo por su nombre.
        estudiante = Estudiante(
            siguiente_id(),
            valores["nombre"], valores["apellido"],
            valores["email"], valores["carnet"],
        )

        # 7) Agrego a la LISTA y guardo
        # Lee la lista actual de registros (lista de diccionarios).
        registros = gestor.leer()
        # Convierte el objeto a diccionario y lo agrega al final de la lista.
        registros.append(estudiante.a_diccionario())
        # guardar() devuelve True/False. Si falló, no se reporta éxito.
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return True, f"Estudiante {estudiante.obtener_nombre_completo()} creado con id {estudiante.id}"

    # 'Exception' atrapa cualquier error; 'as error' guarda su descripción.
    except Exception as error:
        return False, f"Error inesperado: {error}"


# READ 

# Devuelve todos los estudiantes, ya convertidos en objetos Estudiante.
def obtener_todos():
    """LISTA de objetos Estudiante."""
    # Por cada diccionario del archivo crea un objeto con desde_diccionario.
    return [Estudiante.desde_diccionario(registro) for registro in gestor.leer()]


# Busca un estudiante por su id. Devuelve el objeto o None si no existe.
def obtener_por_id(id_estudiante):
    # Búsqueda lineal: recorre uno por uno.
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


#  SEARCH 

# Busca estudiantes cuyo nombre, apellido, email o carnet CONTENGA el término.
def buscar_estudiantes(termino):
    """Búsqueda lineal: revisa registro por registro los campos de CAMPOS_BUSCABLES."""
    # Minúsculas y sin espacios: "ANA", "ana" y " Ana " encuentran lo mismo.
    termino = termino.strip().lower()
    # Término vacío: no se busca nada (sino "" estaría "dentro" de todo texto).
    if not termino:
        return []

    encontrados = []
    # Ciclo externo: cada estudiante (como diccionario) del archivo.
    for registro in gestor.leer():
        # Ciclo interno: cada campo buscable de ESE estudiante (recorre la TUPLA).
        for campo in CAMPOS_BUSCABLES:
            # 'termino in texto' es True si aparece en cualquier parte del texto.
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(Estudiante.desde_diccionario(registro))
                break   # ya coincidió: el break evita agregarlo dos veces
    return encontrados


# ===================== U · UPDATE =====================

# Modifica solo los campos indicados en 'cambios' del estudiante con ese id.
# Ej: actualizar_estudiante(3, {"carnet": "EST2026009"})
def actualizar_estudiante(id_estudiante, cambios):
    """cambios: diccionario solo con los campos que se quieren modificar."""
    try:
        # Un diccionario vacío {} es False: si no hay nada que cambiar, se avisa.
        if not cambios:
            return False, "No se indicó ningún cambio"

        # Normalizo los valores a texto sin espacios sobrantes.
        cambios = {campo: str(valor).strip() for campo, valor in cambios.items()}

        # DIFERENCIA DE CONJUNTOS: ¿mandaron algún campo que no existe?
        # set(cambios) -> conjunto con las CLAVES del diccionario.
        # A - B        -> elementos que están en A pero NO en B.
        # Esto también impide cambiar el "id", porque no está en CAMPOS_ESTUDIANTE.
        desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        # Ningún campo puede quedar vacío al editar.
        vacios = [campo for campo, valor in cambios.items() if not valor]
        if vacios:
            return False, f"Estos campos no pueden quedar vacíos: {', '.join(vacios)}"

        # Si se cambia el email: formato válido y que no lo use OTRO estudiante.
        # excepto_id deja que el estudiante conserve su propio email.
        if "email" in cambios:
            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"
            if cambios["email"].lower() in emails_registrados(excepto_id=id_estudiante):
                return False, "Ese email ya lo usa otro estudiante"

        # Si se cambia el carnet: mayúsculas y que no lo use OTRO estudiante.
        if "carnet" in cambios:
            cambios["carnet"] = cambios["carnet"].upper()
            if cambios["carnet"] in carnets_registrados(excepto_id=id_estudiante):
                return False, "Ese carnet ya lo usa otro estudiante"

        registros = gestor.leer()
        posicion = _posicion_por_id(registros, id_estudiante)

        # Se usa 'is None' (y no 'not posicion') porque el índice 0 es válido
        # pero se evalúa como False: 'not 0' daría True por error.
        if posicion is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        # dict.update(otro) copia las claves de 'cambios' sobre el diccionario:
        # sobrescribe solo esos campos y deja los demás intactos.
        registros[posicion].update(cambios)
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"
        return True, f"Estudiante {id_estudiante} actualizado ({len(cambios)} campo/s)"

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== D · DELETE =====================

# Elimina del archivo al estudiante con ese id.
def eliminar_estudiante(id_estudiante):
    registros = gestor.leer()
    # Construyo una LISTA NUEVA sin ese registro: nunca borro mientras recorro
    # (borrar de una lista mientras se recorre con for hace que Python se
    # salte elementos). Se copian todos MENOS el del id indicado.
    quedan = [registro for registro in registros if registro["id"] != id_estudiante]

    # Si ambas listas miden lo mismo, no se quitó nada: ese id no existía.
    if len(quedan) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"

    if not gestor.guardar(quedan):
        return False, "No se pudo escribir el archivo"
    return True, f"Estudiante {id_estudiante} eliminado"


# ===================== NOTAS, PROMEDIO Y MATERIAS =====================

# Deja el nombre de la materia en un formato único.
# "  matemática " -> "Matemática". Así no se crean dos materias distintas
# solo por escribirlas diferente.
def _normalizar_materia(materia):
    return str(materia).strip().title()


# Agrega una nota a una materia del estudiante. Valida que sea de 0 a 20.
def agregar_nota(id_estudiante, materia, nota):
    """Devuelve (exito, mensaje)."""
    materia = _normalizar_materia(materia)
    if not materia:
        return False, "La materia es obligatoria"

    # Convierte la nota a número. Acepta "18,5" cambiando la coma por punto.
    # float("abc") lanza ValueError: se captura y se devuelve un mensaje.
    try:
        valor = float(str(nota).replace(",", "."))
    except ValueError:
        return False, "La nota debe ser un número"

    # DESEMPAQUETADO de la TUPLA RANGO_NOTA: minimo vale 0 y maximo vale 20.
    minimo, maximo = RANGO_NOTA
    # Comparación encadenada: True solo si minimo <= valor <= maximo.
    # (Con float('nan') también da False, así que se rechaza.)
    if not (minimo <= valor <= maximo):
        return False, f"La nota debe estar entre {minimo} y {maximo}"
    # 18.0 -> 18 (se guarda como entero si no tiene decimales).
    if valor.is_integer():
        valor = int(valor)

    registros = gestor.leer()
    posicion = _posicion_por_id(registros, id_estudiante)
    if posicion is None:
        return False, f"No existe un estudiante con id {id_estudiante}"

    # Diccionario -> objeto, se usa el método del Modelo y objeto -> diccionario.
    # El Modelo se encarga de DICCIONARIO DE LISTAS (notas) y CONJUNTO (materias).
    estudiante = Estudiante.desde_diccionario(registros[posicion])
    estudiante.agregar_nota(materia, valor)
    registros[posicion] = estudiante.a_diccionario()

    if not gestor.guardar(registros):
        return False, "No se pudo escribir el archivo"
    return True, f"Nota {valor} agregada en {materia} a {estudiante.obtener_nombre_completo()}"


# Inscribe al estudiante en una materia sin ponerle nota todavía.
def inscribir_materia(id_estudiante, materia):
    """Devuelve (exito, mensaje)."""
    materia = _normalizar_materia(materia)
    if not materia:
        return False, "La materia es obligatoria"

    registros = gestor.leer()
    posicion = _posicion_por_id(registros, id_estudiante)
    if posicion is None:
        return False, f"No existe un estudiante con id {id_estudiante}"

    estudiante = Estudiante.desde_diccionario(registros[posicion])
    # 'in' sobre un CONJUNTO: pertenencia instantánea.
    if materia in estudiante.materias:
        return False, f"Ya está inscrito en {materia}"

    estudiante.inscribir_materia(materia)
    registros[posicion] = estudiante.a_diccionario()
    if not gestor.guardar(registros):
        return False, "No se pudo escribir el archivo"
    return True, f"{estudiante.obtener_nombre_completo()} inscrito en {materia}"


# Calcula el promedio general y el promedio de cada materia.
def obtener_promedio(id_estudiante):
    """Devuelve (True, resumen) o (False, mensaje). El resumen es un DICCIONARIO."""
    estudiante = obtener_por_id(id_estudiante)
    if estudiante is None:
        return False, f"No existe un estudiante con id {id_estudiante}"

    # COMPRENSIÓN DE DICCIONARIO: {materia: promedio de sus notas}.
    # 'if lista' evita dividir entre cero si una materia no tiene notas.
    por_materia = {
        materia: round(sum(lista) / len(lista), 2)
        for materia, lista in estudiante.notas.items()
        if lista
    }
    return True, {
        "nombre": estudiante.obtener_nombre_completo(),
        "promedio": estudiante.obtener_promedio(),
        "por_materia": por_materia,
    }


# Devuelve el CONJUNTO con todas las materias inscritas por todos los estudiantes.
def materias_ofertadas():
    """Un set no repite: si 5 estudiantes llevan Matemática, aparece una sola vez."""
    ofertadas = set()
    for estudiante in obtener_todos():
        # |= es la UNIÓN de conjuntos (equivale a ofertadas.update(...)).
        ofertadas |= estudiante.materias
    return ofertadas


# Devuelve las materias que comparten dos estudiantes.
def estudiantes_en_comun(id_a, id_b):
    """Devuelve (True, conjunto_de_materias) o (False, mensaje)."""
    if id_a == id_b:
        return False, "Elija dos estudiantes distintos"

    est_a = obtener_por_id(id_a)
    est_b = obtener_por_id(id_b)
    if est_a is None:
        return False, f"No existe un estudiante con id {id_a}"
    if est_b is None:
        return False, f"No existe un estudiante con id {id_b}"

    # INTERSECCIÓN de conjuntos (A & B), hecha dentro del Modelo.
    return True, est_a.materias_en_comun(est_b)


# ------------------------------------------------------------------
# PRUEBA DE LAS FUNCIONES
# Este bloque SOLO se ejecuta si corres este archivo directamente:
#     python views.py
# Si main.py importa este archivo, este bloque NO se ejecuta.
# (Aquí SÍ se usa print() porque es solo una prueba, no parte del Controlador.)
# ------------------------------------------------------------------
if __name__ == "__main__":
    from shared.herramientas import imprimir_titulo, imprimir_info, imprimir_exito

    imprimir_titulo("PRUEBA DE views.py")

    # Usamos un archivo de PRUEBA para no dañar los estudiantes reales.
    gestor = GestorJSON(os.path.join(CARPETA_PROYECTO, "data", "estudiantes_prueba.json"))
    gestor.guardar([])   # empezamos sin estudiantes
    imprimir_info("Se usa el archivo data/estudiantes_prueba.json")

    # ============ 1. crear_estudiante ============
    print("\n===== 1. crear_estudiante =====")
    ana = {"nombre": "Ana", "apellido": "Pérez", "email": "ana@unemi.edu.ec", "carnet": "est2026001"}
    print("Crear a Ana (debe salir True):", crear_estudiante(ana))
    luis = {"nombre": "Luis", "apellido": "Mora", "email": "luis@unemi.edu.ec", "carnet": "EST2026002"}
    print("Crear a Luis (debe salir True):", crear_estudiante(luis))

    repetido_email = {"nombre": "X", "apellido": "Y", "email": "ANA@unemi.edu.ec", "carnet": "EST9"}
    print("Email repetido (debe salir False):", crear_estudiante(repetido_email))
    repetido_carnet = {"nombre": "X", "apellido": "Y", "email": "x@y.com", "carnet": "EST2026001"}
    print("Carnet repetido (debe salir False):", crear_estudiante(repetido_carnet))
    print("Faltan campos (debe salir False):", crear_estudiante({"nombre": "Solo nombre"}))

    # ============ 2. obtener_todos y obtener_por_id ============
    print("\n===== 2. obtener_todos y obtener_por_id =====")
    print("Cantidad (debe salir 2):", len(obtener_todos()))
    print("Id 1 (debe salir Ana):", obtener_por_id(1))
    print("Id 99 (debe salir None):", obtener_por_id(99))

    # ============ 3. buscar_estudiantes ============
    print("\n===== 3. buscar_estudiantes =====")
    print("Buscar 'est2026' (debe salir 2):", len(buscar_estudiantes("est2026")))
    print("Buscar 'luis' (debe salir 1):", len(buscar_estudiantes("luis")))
    print("Buscar 'zzz' (debe salir 0):", len(buscar_estudiantes("zzz")))

    # ============ 4. agregar_nota ============
    print("\n===== 4. agregar_nota =====")
    print("Nota 18 (debe salir True):", agregar_nota(1, "matemática", 18))
    print("Nota '19,5' (debe salir True):", agregar_nota(1, "Matemática", "19,5"))
    print("Nota 21 (debe salir False):", agregar_nota(1, "Inglés", 21))
    print("Nota -1 (debe salir False):", agregar_nota(1, "Inglés", -1))
    print("Nota 'abc' (debe salir False):", agregar_nota(1, "Inglés", "abc"))
    print("Id 99 (debe salir False):", agregar_nota(99, "Inglés", 10))
    print("Nota 15 a Luis (debe salir True):", agregar_nota(2, "Matemática", 15))

    # ============ 5. inscribir_materia y materias_ofertadas ============
    print("\n===== 5. inscribir_materia y materias_ofertadas =====")
    print("Inscribir Luis en Historia (debe salir True):", inscribir_materia(2, "historia"))
    print("Inscribir otra vez (debe salir False):", inscribir_materia(2, "Historia"))
    print("Ofertadas (debe salir Historia y Matemática):", sorted(materias_ofertadas()))

    # ============ 6. obtener_promedio ============
    print("\n===== 6. obtener_promedio =====")
    print("Promedio de Ana (general 18.75):", obtener_promedio(1))
    print("Id 99 (debe salir False):", obtener_promedio(99))

    # ============ 7. estudiantes_en_comun ============
    print("\n===== 7. estudiantes_en_comun =====")
    print("Ana y Luis (debe salir {'Matemática'}):", estudiantes_en_comun(1, 2))
    print("Mismo estudiante (debe salir False):", estudiantes_en_comun(1, 1))
    print("Id 99 (debe salir False):", estudiantes_en_comun(1, 99))

    # ============ 8. actualizar_estudiante ============
    print("\n===== 8. actualizar_estudiante =====")
    print("Cambiar nombre (debe salir True):", actualizar_estudiante(1, {"nombre": "Ana María"}))
    print("Carnet de otro (debe salir False):", actualizar_estudiante(1, {"carnet": "est2026002"}))
    print("Campo inexistente (debe salir False):", actualizar_estudiante(1, {"edad": "20"}))
    print("Id 99 (debe salir False):", actualizar_estudiante(99, {"nombre": "Z"}))

    # ============ 9. eliminar_estudiante ============
    print("\n===== 9. eliminar_estudiante =====")
    print("Eliminar a Luis (debe salir True):", eliminar_estudiante(2))
    print("Eliminar otra vez (debe salir False):", eliminar_estudiante(2))
    print("Quedan (debe salir 1):", len(obtener_todos()))

    # ============ 10. el set de materias sobrevive al JSON ============
    print("\n===== 10. JSON =====")
    print("Materias de Ana leídas del archivo (debe salir {'Matemática'}):", obtener_por_id(1).materias)

    # Al terminar, dejamos el archivo de prueba vacío otra vez.
    gestor.guardar([])
    print()
    imprimir_exito("Fin de las pruebas")
