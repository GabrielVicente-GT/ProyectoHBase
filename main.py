import tkinter as tk
import json
import os

#create "employees", "personal_data", "profesional_data"
#put "employees", "Geoffrey", "personal_data:age", 32


#lo que busco es que al correr mi main y ingresar put "employees", "Geoffrey", "personal_data:age", 32, lo que haga es que primero encuentre si existe un archivo llamdo employees.json y luego de ello en el cree un rowkey que seria Geoffrey, luego revise si existe en el json el personal_data que en este caso si existe dentro de column families y entonces haga que se agregue el age y luego 32 para que al final el json quede algo asi.  {"table_name": "employees", "column_families": ["\"personal_data\"", "\"profesional_data\""]}

def submit_text():
    command = entry.get()
    # si es create
    command_parts = command.split(',')
    if command.startswith('create'):
        
        # print(args)
        table_name = command_parts[0].strip().replace('create ', '').replace('"', '')
        # print("table_name: ", table_name)
        columns = [col.strip() for col in command_parts[1:]]
        create_table(table_name, columns)
        output.config(text=f'Table {table_name} created with columns {columns}')
        
    elif command.startswith('put'):
        print(command_parts)
        table_name = command_parts[0].strip().replace('put ', '').replace('"', '')
        row_key = command_parts[1].strip().replace('"', '')
        column = command_parts[2].split(":")[0].strip().replace('"', '')
        new_value = command_parts[2].split(":")[1].strip().replace('"', '')
        value = command_parts[3].strip()
        print("table_name: ", table_name)
        print("row_key: ", row_key)
        print("column: ", column)
        print("new_value: ",new_value)
        print("value: ", value)
    
        put_data(table_name, column, value)
        output.config(text = f'Row added to table "{table_name}" with row_key {row_key} and column {column} added it variable {new_value} set to {value}\n')
        
    else:
        output.config(text="Comando no reconocido")

# Función para crear la tabla
def create_table(table_name, columns):
    
    table = {
        "table_name": table_name,
        "column_families": columns
    }

    # Crear archivo JSON con la información de la tabla
    with open(f"{table_name}.json", "w") as f:
        json.dump(table, f)

    print(f"Tabla {table_name} creada con éxito.")
    
    # table = {"row_key": []}
    # for column in columns:
    #     table[column] = []
    # with open(f'{table_name}.json', 'w') as f:
    #     json.dump(table, f)
    # print(f'Table {table_name} created with columns: {columns}')
    
    # table = {1: {col: '' for col in columns}}
    # # Eliminar las comillas del nombre de la tabla
    # table_name = table_name.replace('"', '')
    # with open(f'{table_name}.json', 'w') as f:
    #     json.dump(table, f)

#funcion del put
def put_data(table_name, column, value):
    # Leer información de la tabla desde el archivo JSON
    with open(f"{table_name}.json", "r") as f:
        table_info = json.load(f)

    # Extraer el nombre de la column family y la columna
    column_family, column_name = column.split(":")
    print("column_family: ", column_family)
    print("column_name: ", column_name)
    # Verificar si la column family existe
    if column_family not in table_info["column_families"]:
        print(f"Error: la column family '{column_family}' no existe en la tabla.")
        return

    # Leer datos existentes del archivo JSON
    try:
        with open(f"{table_name}/{column_family}/{table_name}.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Agregar valor a la columna correspondiente
    data.setdefault(table_name, {}).setdefault(column_family, {})[column_name] = value

    # Escribir datos actualizados en el archivo JSON
    with open(f"{table_name}/{column_family}/{table_name}.json", "w") as f:
        json.dump(data, f)

    print(f"Valor '{value}' agregado a la columna '{column}' de la fila '{table_name}' con éxito.")







#generacion del interfaz y lectura de texto
root = tk.Tk()

# Crear un cuadro de texto
entry = tk.Entry(root)
entry.pack()

# Crear un botón de submit
submit_button = tk.Button(root, text="Submit", command=submit_text)
submit_button.pack()

# Crear un cuadro de texto para la salida
output = tk.Label(root, text="")
output.pack()

root.mainloop()

