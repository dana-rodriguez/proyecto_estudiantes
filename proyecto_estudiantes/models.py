# NOTA: este archivo es el MODELO del patrón MVC (Modelo-Vista-Controlador).
# Define QUÉ es un estudiante y cómo se convierte a diccionario (para guardarlo
# en JSON) y de diccionario a objeto (al leerlo). No lee archivos, no usa
# print() ni input() en su lógica: eso le toca al Controlador y a la Vista.

# TUPLA de campos: el orden y los nombres son fijos, por eso no es una lista.
# Una tupla es INMUTABLE: nadie puede agregar, quitar ni cambiar campos por error.
# La usan el Controlador (views.py) y la Vista (main.py) para no repetir textos.
# Nota: no incluye "id" (lo genera el sistema) ni "notas"/"materias" (se llenan
# después con agregar_nota() e inscribir_materia(), no al crear el estudiante).
CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet")


# Define la clase Estudiante: el "molde" a partir del cual se crean los objetos.
# Además de datos personales, usa dos estructuras de datos:
# un DICCIONARIO DE LISTAS (notas) y un CONJUNTO (materias).
class Estudiante:
    """Representa a un estudiante, sus materias y sus calificaciones.

    Usa un diccionario de listas para guardar las notas por materia y un
    conjunto para que las materias inscritas no se repitan.
    """

    # __init__ es el CONSTRUCTOR: se ejecuta solo al hacer Estudiante(...).
    # 'notas' y 'materias' valen None por defecto, así que son OPCIONALES.
    # Se usa None (y no {} o set()) porque un valor por defecto mutable se
    # COMPARTIRÍA entre todos los estudiantes creados: error clásico de Python.
    def __init__(self, id_estudiante, nombre, apellido, email, carnet, notas=None, materias=None):
        # Guarda el identificador único. No se llama 'id' el parámetro porque
        # 'id' ya es una función de Python.
        self.id = id_estudiante
        # Guarda los nombres.
        self.nombre = nombre
        # Guarda los apellidos.
        self.apellido = apellido
        # Guarda el correo electrónico.
        self.email = email
        # Guarda el carnet (código académico, texto para conservar ceros iniciales).
        self.carnet = carnet                      # ej: EST2026001
        # DICCIONARIO DE LISTAS: {"Matemática": [18, 19], "Inglés": [17]}
        # Si llegaron notas se usan; si no (None o vacío) se crea un
        # diccionario vacío NUEVO para este estudiante.
        self.notas = notas if notas else {}
        # CONJUNTO: materias en las que está inscrito, sin repetidos.
        # set(materias) convierte cualquier colección (lista, tupla, set) en
        # conjunto y elimina duplicados. Si no llegó nada, queda un set() vacío.
        self.materias = set(materias) if materias else set()

    # Método de INSTANCIA: se llama sobre un objeto ya creado.
    def obtener_nombre_completo(self):
        # f-string: mete nombre y apellido en un solo texto. Ej: "Ana Pérez".
        return f"{self.nombre} {self.apellido}"

    # Agrega una materia al CONJUNTO de materias del estudiante.
    def inscribir_materia(self, materia):
        # add() no duplica: si ya estaba inscrito, no pasa nada.
        self.materias.add(materia)

    # Registra una calificación en una materia.
    def agregar_nota(self, materia, nota):
        # Primero asegura la inscripción (si ya estaba, no pasa nada).
        self.inscribir_materia(materia)
        # setdefault(materia, []) devuelve la lista de esa materia; si la
        # materia no existía, crea la clave con [] y devuelve esa lista nueva.
        # Luego .append(nota) agrega la nota al final de esa lista.
        # Ej: {} -> {"Matemática": [18]} -> {"Matemática": [18, 19]}
        self.notas.setdefault(materia, []).append(nota)

    # Calcula el promedio general juntando las notas de TODAS las materias.
    def obtener_promedio(self):
        # Lista plana donde se juntan todas las notas, sin importar la materia.
        todas = []
        # self.notas.values() recorre solo las LISTAS de notas del diccionario.
        for lista_notas in self.notas.values():
            # extend() agrega CADA elemento (append agregaría la lista entera).
            todas.extend(lista_notas)
        # Una lista vacía es False: sin notas se devuelve 0 y se evita
        # dividir entre cero.
        if not todas:
            return 0
        # sum() suma, len() cuenta; su división es el promedio.
        # round(..., 2) lo deja con 2 decimales.
        # IMPORTANTE: se devuelve SOLO el número (no una tupla).
        return round(sum(todas) / len(todas), 2)

    # Devuelve las materias que este estudiante comparte con otro.
    def materias_en_comun(self, otro_estudiante):
        # INTERSECCIÓN de conjuntos: el operador & equivale a
        # self.materias.intersection(otro_estudiante.materias).
        # Ej: {"Física", "Matemática"} & {"Matemática", "Inglés"} -> {"Matemática"}
        return self.materias & otro_estudiante.materias

    # Convierte el objeto en un diccionario (json.dump no guarda objetos).
    def a_diccionario(self):
        # Objeto -> diccionario (listo para JSON). Cada "clave": valor toma
        # un atributo del objeto.
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "carnet": self.carnet,
            "notas": self.notas,       # dict de listas: SÍ es compatible con JSON
            # JSON no sabe guardar un set: lo convertimos a lista ordenada.
            # sorted() devuelve una LISTA alfabética, así el archivo siempre
            # queda igual y es fácil de leer.
            "materias": sorted(self.materias),
        }

    # @classmethod: método de CLASE. Recibe 'cls' (la clase Estudiante) en vez
    # de 'self'. Sirve de "constructor alternativo" para crear un Estudiante
    # desde un diccionario: Estudiante.desde_diccionario({...})
    @classmethod
    def desde_diccionario(cls, datos):
        # cls(...) equivale a Estudiante(...): llama al constructor __init__.
        return cls(
            # Campos obligatorios: con [] (si faltan, lanza KeyError).
            datos["id"], datos["nombre"], datos["apellido"], datos["email"],
            datos["carnet"],
            # Argumentos por NOMBRE. .get devuelve el valor por defecto si
            # la clave no existe (no da error).
            notas=datos.get("notas", {}),
            # En el JSON las materias son una lista; set() las regresa a conjunto.
            materias=set(datos.get("materias", [])),
        )

    # __str__ es un método "mágico": Python lo llama con print(estudiante).
    def __str__(self):
        # Ej: "[EST2026001] Ana Pérez - Promedio: 18.5"
        return f"[{self.carnet}] {self.obtener_nombre_completo()} - Promedio: {self.obtener_promedio()}"


# ------------------------------------------------------------------
# PRUEBA RÁPIDA DE LA CLASE
# Este bloque SOLO se ejecuta con:  python models.py
# Si otro archivo importa models, este bloque NO se ejecuta.
# ------------------------------------------------------------------
if __name__ == "__main__":
    est1 = Estudiante(1, "Ana", "Pérez", "ana@unemi.edu.ec", "EST2026001")
    est2 = Estudiante(2, "Luis", "Mora", "luis@unemi.edu.ec", "EST2026002")

    print("--- obtener_nombre_completo (debe salir Ana Pérez) ---")
    print(est1.obtener_nombre_completo())

    print("\n--- obtener_promedio sin notas (debe salir 0) ---")
    print(est1.obtener_promedio())

    print("\n--- inscribir_materia: Física repetida no se duplica (debe salir {'Física'}) ---")
    est1.inscribir_materia("Física")
    est1.inscribir_materia("Física")
    print(est1.materias)

    print("\n--- agregar_nota (también inscribe la materia) ---")
    est1.agregar_nota("Matemática", 18)
    est1.agregar_nota("Matemática", 19)
    est1.agregar_nota("Inglés", 17)
    est2.agregar_nota("Matemática", 15)
    est2.agregar_nota("Programación", 20)
    print("est1 notas:", est1.notas)
    print("est2 notas:", est2.notas)

    print("\n--- obtener_promedio (est1 debe salir 18.0 y est2 17.5) ---")
    print("est1:", est1.obtener_promedio())
    print("est2:", est2.obtener_promedio())

    print("\n--- materias_en_comun (debe salir {'Matemática'}) ---")
    print(est1.materias_en_comun(est2))

    print("\n--- a_diccionario y desde_diccionario ---")
    datos = est1.a_diccionario()
    print(datos)
    copia = Estudiante.desde_diccionario(datos)
    print("¿Mismas notas? (True):", copia.notas == est1.notas)
    print("¿Mismas materias? (True):", copia.materias == est1.materias)

    print("\n--- __str__ ---")
    print(est1)
    print(est2)
