import tkinter as tk
import json
import os
import time

#create "employees", "personal_data", "profesional_data"
#put "employees", "Geoffrey", "personal_data:age", 32
#alter "employees", { NAME => "profesional_data", VERSIONS => 3 }

data_dir = "data"

def submit_text():
    command = entry.get()
    command_parts = command.split(',')
    #comando de create
    if command.startswith('create'):
        # print(args)
        table_name = command_parts[0].replace('create ', '').replace('"', '').replace("'", '').strip()
        columns = [col.replace('"', '').replace("'", '').strip() for col in command_parts[1:]]
        # print("table_name: ", table_name)
        # print("columns: ", columns)
        create_table(table_name, columns)
    #comando de put
    elif command.startswith('put'):
        # print(command_parts)
        table_name = command_parts[0].replace('put ', '').replace('"', '').replace("'", '').strip()
        row_key = command_parts[1].replace('"', '').replace("'", '').strip()
        column = command_parts[2].replace('"', '').replace("'", '').strip()
        value = command_parts[3].replace('"', '').replace("'", '').strip()
        # print("table_name: ", table_name)
        # print("row_key: ", row_key)
        # print("column: ", column)
        # print("value: ", value)
    
        put_data(table_name, row_key, column, value)
    #para deshabilitar la tabla
    elif command.startswith('disable'):
        table_name = command.replace("disable", '').replace('"','').replace("'", '').strip()
        # print("table_name: ", table_name)
        table_state(table_name,False)
    #para habilitar la tabla
    elif command.startswith('enable') or command.startswith('Is_Enable'):
        table_name = command.replace("enable", '').replace("Is_Enable", '').replace('"','').replace("'", '').strip()
        table_state(table_name,True)
    #alter command
    elif command.startswith('alter'):
        table_name = command_parts[0].replace("alter", '').replace('"','').replace("'", '').strip()
        column = command_parts[1].replace("NAME", '').replace("=>", '').replace("{", '').replace('"','').replace("'", '').strip()
        values = command_parts[2].split("=>")
        data = values[0].strip()
        value = values[1].replace("}","").strip()
        # print(table_name)
        # print(column)
        # print(data)
        # print(value)
        alter_table(table_name,column,data,value)
        
    else:
        output.config(text="Comando no reconocido")



#para crear una tabla
def create_table(table_name, columns):
    timestamp = int(time.time()*1000)
    
    column = {}
    for x in columns:
        column[x]={"DATA_BLOCK_ENCODING":"NONE", "BLOOMFILTER":"ROW", "REPLICATION_SCOPE":"0", "VERSIONS":"1", "COMPRESSION":"NONE",}
    
    table_data = {"columns": column, "state":True ,"rows": {}, "created_timestamp":timestamp, "updated_timestamp":timestamp}
    if not os.path.exists(data_dir):
        os.makedirs('data')
    table_file = os.path.join(data_dir, f"{table_name}.json")
    if not os.path.exists(table_file):
        with open(table_file, "w") as f:
            json.dump(table_data, f)
        # print(f"Table '{table_name}' created with columns: {columns}")
        output.config(text=f'Table "{table_name}" created with columns "{column}"')
    else:
        # print(f"Table '{table_name}' already exists")
        output.config(text=f'Table "{table_name}" already exists')

#para agregar datos a la tabla
def put_data(table_name, row_key, column, value):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.config(text = f"Table '{table_name}' does not exist.")
        return

    with open(table_file, "r") as f:
        table_data = json.load(f)
    #revisa su estado si esta disable o enable
    if table_data["state"] == False:
        output.config(text = f"Table '{table_name}' is disable.")
        return

    # revisa si la columna existe
    column_family, qualifier = column.split(":")
    if column_family not in table_data["columns"]:
        # print(f"Column '{column}' does not exist in table '{table_name}'.")
        output.config(text = f"Column '{column}' does not exist in table '{table_name}'.")
        return

    if row_key not in table_data["rows"]:
        table_data["rows"][row_key] = {}

    if column_family not in table_data["rows"][row_key]:
        table_data["rows"][row_key][column_family] = {}
    
    #actualizar el timestamp de la tabla
    timestamp = int(time.time()*1000)
    table_data["updated_timestamp"] = timestamp
    
    
    table_data["rows"][row_key][column_family][qualifier] =  {"value": str(value), "timestamp": timestamp}
    #ordenarlos 
    table_data["rows"] = dict(sorted(table_data["rows"].items()))

    # print(table_data)

    with open(table_file, "w") as f:
        json.dump(table_data, f)

    # print(f"Data added to table '{table_name}' for row '{row_key}', column '{column}'.")
    output.config(text = f'Row added to table "{table_name}" with row_key "{row_key}" and column "{column}" set to "{value}"\n')


#para disable o enable la tabla
def table_state(table_name, state):
    # print(table_name)
    table_file = os.path.join(data_dir, f"{table_name}.json")

    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.config(text = f"Table '{table_name}' does not exist.")
        return
    
    with open(table_file, "r") as f:
        table_data = json.load(f)

    table_data['state'] = state
    #actualizar el timestamp de la tabla
    timestamp = int(time.time()*1000)
    table_data["updated_timestamp"] = timestamp

    with open(table_file, "w") as f:
        json.dump(table_data, f)

    if state == True:
        text = "enable"
    else:
        text = "disable"

    output.config(text = f'Table "{table_name}" state is {text}\n')
    
#para alterar la tabla
def alter_table(table_name, column, data, value):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    
    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.config(text = f"Table '{table_name}' does not exist.")
        return
    
    with open(table_file, "r") as f:
        table_data = json.load(f)
    
    if column not in table_data["columns"]:
        # print(f"Column '{column}' does not exist in table '{table_name}'.")
        output.config(text = f"Column '{column}' does not exist in table '{table_name}'.")
        return
    
    if data not in table_data["columns"][column]:
        output.config(text = f"Data '{data}' does not exist in column '{column}' of table '{table_name}'.")
        return
    
    table_data["columns"][column][data] = str(value)
    
    
    timestamp = int(time.time()*1000)
    table_data["updated_timestamp"] = timestamp
    
    with open(table_file, "w") as f:
        json.dump(table_data, f)
    output.config(text = f'Table "{table_name}" column "{column}" data "{data}" succesfully changed to "{value}."\n')


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

