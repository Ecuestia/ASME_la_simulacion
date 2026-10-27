#Usando el cadáver del omnicrane junto con el ejemplo básico de Tkinter:
#________________________________________________________________________-
# Este programa tiene como propósito aportar una interfaz gráfica para
# futuros códigos que sean ejecutables
#________________________________________________________________________-
#PARA GRÁFICAS
import matplotlib.pyplot as plt
#PARA LA INTERFAZ
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

ARCHIVO = "PRUEBA 1.dwxml"

def listar_archivos_carpeta():
    carpeta = Path(__file__).parent
    return sorted(
        archivo.name
        for archivo in carpeta.iterdir()
        if archivo.is_file() and archivo.suffix.lower() in {".dwxml", ".dwxmz"}
    )


def leer_raiz_documento(ruta_archivo):
    extension = ruta_archivo.suffix.lower()
    if extension == ".dwxml":
        raiz = ET.parse(ruta_archivo).getroot()
    elif extension == ".dwxmz":
        with ZipFile(ruta_archivo) as archivo_comprimido:
            miembros_dwxml = [
                nombre
                for nombre in archivo_comprimido.namelist()
                if nombre.lower().endswith(".dwxml")
            ]
            miembros_xml = [
                nombre
                for nombre in archivo_comprimido.namelist()
                if nombre.lower().endswith(".xml")
            ]
            miembros = miembros_dwxml or miembros_xml
            if not miembros:
                raise ValueError(
                    "El archivo .dwxmz no contiene un documento XML."
                )
            if len(miembros) > 1:
                raise ValueError(
                    "El archivo .dwxmz contiene varios documentos XML; "
                    "no se puede determinar cuál cargar."
                )
            raiz = ET.fromstring(archivo_comprimido.read(miembros[0]))
    else:
        raise ValueError("Formato no compatible. Selecciona un archivo .dwxml o .dwxmz.")

    if raiz.tag != "DWSIM_Simulation_Data":
        raise ValueError("El archivo no tiene la raíz XML esperada de DWSIM.")
    return raiz


def extraer_sistema_unidades(raiz):
    sistema = raiz.findtext("Settings/SelectedUnitSystem1/Type")
    if not sistema:
        raise ValueError("No se encontró el sistema de unidades en Settings.")
    return sistema


def extraer_operaciones(raiz):
    nombres_operacion = {
        "DWSIM.UnitOperations.Reactors.Reactor_Gibbs": "Reactor de Gibbs",
        "DWSIM.UnitOperations.Reactors.Reactor_Equilibrium":
            "Reactor de equilibrio",
    }
    identificadores_y_tipos = []
    for objeto in raiz.findall("SimulationObjects/SimulationObject"):
        tipo = objeto.findtext("Type")
        if tipo and tipo.startswith("DWSIM.UnitOperations.") and ".Streams." not in tipo:
            identificador = objeto.findtext("Name")
            if not identificador:
                raise ValueError("Se encontró una operación sin identificador Name.")
            nombre_tipo = nombres_operacion.get(tipo, tipo.rsplit(".", 1)[-1])
            identificadores_y_tipos.append((identificador, nombre_tipo))

    ids_operaciones = {
        identificador for identificador, _ in identificadores_y_tipos
    }
    etiquetas_por_id = {
        objeto.findtext("Name"): objeto.findtext("Tag")
        for objeto in raiz.findall("GraphicObjects/GraphicObject")
        if objeto.findtext("Name") in ids_operaciones
    }
    operaciones = {}
    for identificador, nombre_tipo in identificadores_y_tipos:
        etiqueta = etiquetas_por_id.get(identificador)
        if etiqueta is None:
            raise ValueError(
                f"No se encontró un Tag gráfico para la operación {identificador}."
            )
        operaciones[identificador] = {
            "tag": etiqueta,
            "tipo": nombre_tipo,
        }
    return operaciones

def extraer_corrientes(raiz):
    tipo_corriente = "DWSIM.Thermodynamics.Streams.MaterialStream"
    identificadores = []
    for objeto in raiz.findall("SimulationObjects/SimulationObject"):
        if objeto.findtext("Type") == tipo_corriente:
            identificador = objeto.findtext("Name")
            if not identificador:
                raise ValueError("Se encontró una corriente sin identificador Name.")
            identificadores.append(identificador)

    etiquetas_por_id = {
        objeto.findtext("Name"): objeto.findtext("Tag")
        for objeto in raiz.findall("GraphicObjects/GraphicObject")
        if objeto.findtext("Name") in identificadores
    }
    corrientes = {}
    for identificador in identificadores:
        etiqueta = etiquetas_por_id.get(identificador)
        if etiqueta is None:
            raise ValueError(
                f"No se encontró un Tag gráfico para la corriente {identificador}."
            )
        corrientes[identificador] = etiqueta
    return corrientes




def cargar_datos_archivo(nombre_archivo):
    ruta_archivo = Path(__file__).with_name(nombre_archivo)
    raiz = leer_raiz_documento(ruta_archivo)
    sistema_unidades = extraer_sistema_unidades(raiz)
    corrientes = extraer_corrientes(raiz)
    operaciones = extraer_operaciones(raiz)
    return sistema_unidades, corrientes, operaciones


SistemaUnidades, CorrientesPorID, OperacionesPorID = cargar_datos_archivo(ARCHIVO)
SI_ENG_aparece = "SI_ENG" in SistemaUnidades
NumeroCorrientes = len(CorrientesPorID)
NumeroOperaciones = len(OperacionesPorID)

# NOMBRE DE LA ACTIVIDAD
NOMBRE="Diseño mecánico de equipo de procesos"

#COLORES DEL PROGRAMA
SOLVER = "#e12885"
TEXTO = "#a3c0da"
DIALOGO = "#137a7f"
FONDO = "#86cecb"
FORMA1 = "#373b3e"
#TAMAÑOS DE LETRA
TÍTULOS = 20
SUBTÍTULOS = 16
PESTAÑAS = 10   
TEXTOS = 12
LETRA = [TEXTOS, PESTAÑAS, SUBTÍTULOS, TÍTULOS]


MenuPrincipal=tkinter.Tk()
MenuPrincipal.title(NOMBRE)
MenuPrincipal.configure(bg=FONDO)
MenuPrincipal.geometry()
notebook = ttk.Notebook(MenuPrincipal)
notebook.pack(fill="both", expand=True, padx=10, pady=10)
#CATEGORÍAS DE PESTAÑAS
DOCUMENTO = tkinter.Frame(notebook, bg=TEXTO)
EQUIPOS = tkinter.Frame(notebook, bg=TEXTO)
CORRIENTES = tkinter.Frame(notebook, bg=TEXTO)
MATERIALES = tkinter.Frame(notebook, bg=TEXTO)
RESULTADOS = tkinter.Frame(notebook, bg=TEXTO)
CATEGORÍAS = [
    (DOCUMENTO, "Archivo",2),
    (EQUIPOS, "Equipos",9),
    (CORRIENTES, "Corrientes",9),
    (MATERIALES, "Materiales",8),
    (RESULTADOS, "Resultados",2),
]
for pestaña, texto_pestaña, columnas in CATEGORÍAS:

    notebook.add(pestaña, text=texto_pestaña)
    
    for fila in range(5):
        pestaña.rowconfigure(fila, weight=1)

    for columnas in range(columnas):
        pestaña.columnconfigure(columnas, weight=1)

def actualizar_corrientes():
    for widget in CORRIENTES.winfo_children():
        widget.destroy()

    ttk.Label(
        CORRIENTES,
        text=f"Número de corrientes: {NumeroCorrientes}",
        background=TEXTO,
        font=("Arial", TÍTULOS, "bold"),
    ).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ttk.Label(CORRIENTES, text="Tag", background=TEXTO).grid(
        row=1,
        column=0,
        sticky="w",
        padx=10,
        pady=5,
    )
    for fila, etiqueta in enumerate(CorrientesPorID.values(), start=2):
        ttk.Label(CORRIENTES, text=etiqueta, background=TEXTO).grid(
            row=fila,
            column=0,
            sticky="w",
            padx=10,
            pady=5,
        )


def actualizar_equipos():
    for widget in EQUIPOS.winfo_children():
        widget.destroy()

    ttk.Label(
        EQUIPOS,
        text=f"Número de operaciones: {NumeroOperaciones}",
        background=TEXTO,
        font=("Arial", TÍTULOS, "bold"),
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    ttk.Label(EQUIPOS, text="Tag", background=TEXTO).grid(
        row=1,
        column=0,
        sticky="w",
        padx=10,
        pady=5,
    )
    ttk.Label(EQUIPOS, text="Tipo de operación", background=TEXTO).grid(
        row=1,
        column=1,
        sticky="w",
        padx=10,
        pady=5,
    )
    for fila, operacion in enumerate(OperacionesPorID.values(), start=2):
        ttk.Label(EQUIPOS, text=operacion["tag"], background=TEXTO).grid(
            row=fila,
            column=0,
            sticky="w",
            padx=10,
            pady=5,
        )
        ttk.Label(EQUIPOS, text=operacion["tipo"], background=TEXTO).grid(
            row=fila,
            column=1,
            sticky="w",
            padx=10,
            pady=5,
        )


def comando_maestro():
    global ARCHIVO, SistemaUnidades, SI_ENG_aparece
    global CorrientesPorID, NumeroCorrientes, OperacionesPorID, NumeroOperaciones

    archivo_seleccionado = ArchivoCombo.get()
    if not archivo_seleccionado:
        messagebox.showerror("Archivo requerido", "Selecciona un archivo.")
        return

    try:
        datos = cargar_datos_archivo(archivo_seleccionado)
    except (BadZipFile, ET.ParseError, OSError, RuntimeError, ValueError) as error:
        messagebox.showerror(
            "No se pudo leer el archivo",
            f"No se pudo cargar {archivo_seleccionado}:\n{error}",
        )
        ArchivoCombo.set(ARCHIVO)
        return

    ARCHIVO = archivo_seleccionado
    SistemaUnidades, CorrientesPorID, OperacionesPorID = datos
    SI_ENG_aparece = "SI_ENG" in SistemaUnidades
    NumeroCorrientes = len(CorrientesPorID)
    NumeroOperaciones = len(OperacionesPorID)
    EtiquetaNombreArchivo.config(text=f"Nombre del archivo: {ARCHIVO}")
    EtiquetaRutaArchivo.config(
        text=f"Ruta del archivo: {Path(__file__).with_name(ARCHIVO)}"
    )
    actualizar_corrientes()
    actualizar_equipos()


ttk.Label(
    DOCUMENTO,
    text="Archivo del mismo directorio:",
    background=TEXTO,
).grid(row=0, column=0, sticky="w", padx=10, pady=5)
ArchivoCombo = ttk.Combobox(
    DOCUMENTO,
    values=listar_archivos_carpeta(),
    state="readonly",
    width=40,
)
ArchivoCombo.set(ARCHIVO)
ArchivoCombo.grid(row=0, column=1, sticky="w", padx=10, pady=5)
ttk.Button(
    DOCUMENTO,
    text="Cargar documento",
    command=comando_maestro,
).grid(row=0, column=2, sticky="w", padx=10, pady=5)

EtiquetaNombreArchivo = ttk.Label(
    DOCUMENTO,
    text=f"Nombre del archivo: {ARCHIVO}",
    background=TEXTO,
    font=("Arial", TÍTULOS, "bold"),
)
EtiquetaNombreArchivo.grid(
    row=1,
    column=0,
    columnspan=3,
    sticky="w",
    padx=10,
    pady=5,
)
EtiquetaRutaArchivo = ttk.Label(
    DOCUMENTO,
    text=f"Ruta del archivo: {Path(__file__).with_name(ARCHIVO)}",
    background=TEXTO,
)
EtiquetaRutaArchivo.grid(
    row=2,
    column=0,
    columnspan=3,
    sticky="w",
    padx=10,
    pady=5,
)

actualizar_corrientes()
actualizar_equipos()

MenuPrincipal.mainloop()