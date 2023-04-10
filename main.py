import tkinter as tk
import json
import os

#create "employees", "personal_data", "profesional_data"
#put "employees", "Geoffrey", "personal_data:age", 32


#lo que busco es que al correr mi main y ingresar put "employees", "Geoffrey", "personal_data:age", 32, lo que haga es que primero encuentre si existe un archivo llamdo employees.json y luego de ello en el cree un rowkey que seria Geoffrey, luego revise si existe en el json el personal_data que en este caso si existe dentro de column families y entonces haga que se agregue el age y luego 32 para que al final el json quede algo asi.  {"table_name": "employees", "column_families": ["\"personal_data\"", "\"profesional_data\""]}
data_dir = "data"

def submit_text():
    command = entry.get()
    # si es create
    command_parts = command.split(',')
    if command.startswith('create'):
        
        # print(args)
        table_name = command_parts[0].strip().replace('create ', '').replace('"', '')
        columns = [col.strip().replace('"', '') for col in command_parts[1:]]
        print("table_name: ", table_name)
        print("columns: ", columns)
        create_table(table_name, columns)
        output.config(text=f'Table {table_name} created with columns {columns}')
        
    elif command.startswith('put'):
        print(command_parts)
        table_name = command_parts[0].strip().replace('put ', '').replace('"', '')
        row_key = command_parts[1].strip().replace('"', '')
        column = command_parts[2].strip().replace('"', '')
        value = command_parts[3].strip().replace('"', '')
        print("table_name: ", table_name)
        print("row_key: ", row_key)
        print("column: ", column)
        print("value: ", value)
    
        put_data(table_name, row_key, column, value)
        output.config(text = f'Row added to table "{table_name}" with row_key {row_key} and column {column} set to {value}\n')
        
    else:
        output.config(text="Comando no reconocido")

def create_table(table_name, columns):
    table_data = {"columns": columns, "rows": {}}
    if not os.path.exists(data_dir):
        os.makedirs('data')
    table_file = os.path.join(data_dir, f"{table_name}.json")
    with open(table_file, "w") as f:
        json.dump(table_data, f)
    print(f"Table '{table_name}' created with columns: {columns}")


def put_data(table_name, row_key, column, value):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    if not os.path.exists(table_file):
        print(f"Table '{table_name}' does not exist.")
        return

    with open(table_file, "r") as f:
        table_data = json.load(f)

    print(table_data)
    print(table_data["columns"])
    column_family, qualifier = column.split(":")
    if column_family not in table_data["columns"]:
        print(f"Column '{column}' does not exist in table '{table_name}'.")
        return

    if row_key not in table_data["rows"]:
        table_data["rows"][row_key] = {}

    if column_family not in table_data["rows"][row_key]:
        table_data["rows"][row_key][column_family] = {}

    table_data["rows"][row_key][column_family][qualifier] = str(value)

    with open(table_file, "w") as f:
        json.dump(table_data, f)

    print(f"Data added to table '{table_name}' for row '{row_key}', column '{column}'.")








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

