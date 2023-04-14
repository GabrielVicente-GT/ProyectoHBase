import tkinter as tk
import json
import os
import time
import re
from tabulate import *

#create "employees", "personal_data", "profesional_data"
#put "employees", "Geoffrey", "personal_data:age", 32
#alter "employees", { NAME => "profesional_data", VERSIONS => 3 }
# alter "employees", { NAME => "profesional_data", VERSIONS => 3 , REPLICATION_SCOPE => 8 }
# put 'employees', 'Tomas', 'personal_data:age', 15 , 'Yong', 'personal_data:age', 18, 'Yong', 'profesional_data:position', 'intern'
# get "employees", "Yong"
# get "employees", "Yong", { COLUMN => "personal_data:age" }
# get "employees", "Yong", { COLUMN => "personal_data:age", VERSIONS => 3 }

data_dir = "data"

def submit_text():
    clear_output_text()
    command = entry.get()
    
    # Reemplazar espacios dentro de las llaves para evitar separaciones internas
    command = re.sub(r"{\s*(\w+)\s*=>", r"{\g<1>=>", command)
    
    # Dividir la cadena en comas que no estén dentro de llaves
    split_parts = re.findall(r"[^,{}]+(?:\{[^{}]*\})*", command)

    # Eliminar espacios en los extremos de cada parte y regresar una lista
    command_parts = [part.strip() for part in split_parts if part.strip()]
    # Eliminar cadenas vacias
    command_parts = [part for part in command_parts if bool(part)]
    
    # print(command_parts)
    # print(len(command_parts))
    # for i in range(len(command_parts)):
    #     print(command_parts[i])
    # print("==========================")
    #comando de create
    if command.startswith('create'):
        # print(args)
        table_name = command_parts[0].replace('create ', '').replace('"', '').replace("'", '').strip()
        columns = [col.replace('"', '').replace("'", '').strip() for col in command_parts[1:]]
        # print("table_name: ", table_name)
        # print("columns: ", columns)
        create_table(table_name, columns)
        
    #comando de put que funciona igual tambien para insertMany
    elif command.startswith('put'):
        # print(command_parts)
        table_name = command_parts[0].replace('put ', '').replace('"', '').replace("'", '').strip()
        #encontrar  todos los rowkeys
        i = 1
        array_row_key = []
        seguir = True
        while(seguir):
            if i < len(command_parts):
                array_row_key.append(command_parts[i].replace('"', '').replace("'", '').strip())
                i += 3
            else:
                seguir=False
        
        #encontrar  todos los column
        i = 2
        array_column = []
        seguir = True
        while(seguir):
            if i < len(command_parts):
                array_column.append(command_parts[i].replace('"', '').replace("'", '').strip())
                i += 3
            else:
                seguir=False

        #encontrar  todos los value
        i = 3
        array_value = []
        seguir = True
        while(seguir):
            if i < len(command_parts):
                array_value.append(command_parts[i].replace('"', '').replace("'", '').strip())
                i += 3
            else:
                seguir=False

        #revisar que todos tengan el mismo len de lo contrario significa que falta algun dato
        rowKeyLen = len(array_row_key)
        columLen = len(array_column)
        valueLen = len(array_value)

        # print("table_name: ", table_name)
        # print("row_key: ", array_row_key)
        # print("column: ", array_column)
        # print("value: ", array_value)
        
        if rowKeyLen == columLen == valueLen:
            for l in range(rowKeyLen):
                put_data(table_name,array_row_key[l],array_column[l],array_value[l])
            

        else:
            output.insert('end',f'Error, falta algun argumento')
        # print("table_name: ", table_name)
        # print("row_key: ", row_key)
        # print("column: ", column)
        # print("value: ", value)
        
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
        table_name = command_parts[0].replace("alter", '').replace('"','').replace("'", '').replace(",", '').strip()
        columns = command_parts[1].replace("{", '').replace("}","").replace('"','').replace("'", '').split(",")
        parts = columns.pop(0).split("=>")
        column = parts[1].replace('"','').replace("'", '').strip()
        data = []
        value = []
        for l in range(len(columns)):
            parts = columns[l].split("=>")
            data.append(parts[0].replace('"','').replace("'", '').strip())
            value.append(parts[1].replace('"','').replace("'", '').strip())
        
        # print("table_name: ", table_name)
        # print("column: ", column)
        # print("data: ", data)
        # print("value: ",value)
        
        for l in range(len(data)):
            alter_table(table_name,column,data[l],value[l])
        
    #scan command
    elif command.startswith("scan"):
        table_name = command.replace("scan", '').replace('"','').replace("'", '').strip()
        scan_table(table_name)
    
    #drop command
    elif command.startswith("drop"):
        table_name = command.replace("drop", '').replace('"','').replace("'", '').strip()
        drop_function(table_name)
    
    #describe command
    elif command.startswith("describe"):
        table_name = command.replace("describe", '').replace('"','').replace("'", '').strip()
        describe_function(table_name)
        
    #get command
    elif command.startswith("get"):
        # print(command_parts)
        table_name = ""
        row = ""
        columns = ""
        table_name = command_parts[0].replace("get", '').replace('"','').replace("'", '').replace(",", '').strip()
        if len(command_parts) == 2:
            row = command_parts[1].replace('"','').replace("'", '').strip()
            # print("table_name: ", table_name)
            # print("row: ", row)
            # print("columns: ", columns)
            get_table(table_name,row,columns)
        elif len(command_parts) == 3:
            row = command_parts[1].replace('"','').replace("'", '').strip()
            columns = command_parts[2].replace("{","").replace("}","").split(",")
            # print("table_name: ", table_name)
            # print("row: ", row)
            # print("columns: ", columns)
            get_table(table_name,row,columns)
        else:
            output.insert("Error, Missing Values")
    
        
    # No existe el comando
    else:
        output.insert('end',"Comando no reconocido")
    

def clear_output_text():
    output.delete('1.0', tk.END)

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
        output.insert('end',f'Table "{table_name}" created with columns "{column}"')
    else:
        # print(f"Table '{table_name}' already exists")
        output.insert('end',f'Table "{table_name}" already exists')

#Función que hace el drop de un HBase
def drop_function(table_name):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    if table_file["state"] == False:
        output.insert('end',f"Table '{table_name}' is disable.")
        return

    if os.path.exists(table_file):
        os.remove(table_file)
        output.insert('end',f'Table "{table_name}" dropped')
    else:
        output.insert('end',f'Table "{table_name}" does not exist')
        
def describe_function(table_name):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    if table_file["state"] == False:
        output.insert('end',f"Table '{table_name}' is disable.")
        return
    if os.path.exists(table_file):
        with open(table_file, "r") as f:
            table_data = json.load(f)
        headers = ["Column Family", "Column", "Version", "Block Encoding", "Compression", "Bloom Filter", "Replication Scope"]
        data = []
        for column in table_data["columns"]:
            temporalArray = []
            # print("Valores de la columna: ", column)
            temporalArray.append(column)
            # data.append([column])
            for key, value in table_data["columns"][column].items():
                # print("key: ", key)
                # print("value: ", value)
                temporalArray.append(value)
                # data.append([key, value])
            data.append(temporalArray)
        # print(data)
        table = tabulate(data, headers=headers, tablefmt="pretty")
        output.insert('end',f'Table "{table_name}"')
        output.insert('end',table)
    else:
        output.insert('end',f'Table "{table_name}" does not exist')
                

#para agregar datos a la tabla
def put_data(table_name, row_key, column, value):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.insert('end',f"Table '{table_name}' does not exist.")
        return

    with open(table_file, "r") as f:
        table_data = json.load(f)
    #revisa su estado si esta disable o enable
    if table_data["state"] == False:
        output.insert('end',f"Table '{table_name}' is disable.")
        return

    # revisa si la columna existe
    column_family, qualifier = column.split(":")
    if column_family not in table_data["columns"]:
        # print(f"Column '{column}' does not exist in table '{table_name}'.")
        output.insert('end',f"Column '{column}' does not exist in table '{table_name}'.")
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
    output.insert('end',f'Row added to table "{table_name}" with row_key "{row_key}" and column "{column}" set to "{value}"\n')


#para disable o enable la tabla
def table_state(table_name, state):
    # print(table_name)
    table_file = os.path.join(data_dir, f"{table_name}.json")

    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.insert('end',f"Table '{table_name}' does not exist.")
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

    output.insert('end', f'Table "{table_name}" state is {text}\n')
    
#para alterar la tabla
def alter_table(table_name, column, data, value):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    
    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.insert('end', f"Table '{table_name}' does not exist.")
        return
    
    with open(table_file, "r") as f:
        table_data = json.load(f)

    #revisa su estado si esta disable o enable
    if table_data["state"] == False:
        output.insert('end',f"Table '{table_name}' is disable.")
        return
    
    if column not in table_data["columns"]:
        # print(f"Column '{column}' does not exist in table '{table_name}'.")
        output.insert('end', f"Column '{column}' does not exist in table '{table_name}'.")
        return
    
    if data not in table_data["columns"][column]:
        output.insert('end', f"Data '{data}' does not exist in column '{column}' of table '{table_name}'.")
        return
    
    table_data["columns"][column][data] = str(value)
    
    
    timestamp = int(time.time()*1000)
    table_data["updated_timestamp"] = timestamp
    
    with open(table_file, "w") as f:
        json.dump(table_data, f)
    output.insert('end', f'Table "{table_name}" column "{column}" data "{data}" succesfully changed to "{value}."\n')
    
    
    
#para obtener todos los valores de la tabla
def scan_table(table_name):
    table_file = os.path.join(data_dir, f"{table_name}.json")
    
    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.insert('end', f"Table '{table_name}' does not exist.")
        return
    
    with open(table_file, "r") as f:
        table_data = json.load(f)

    #revisa su estado si esta disable o enable
    if table_data["state"] == False:
        output.insert('end',f"Table '{table_name}' is disable.")
        return
        
    # print(table_data)
    output.insert('end', "{:<20} {:<30}\n".format("ROW", "COLUMN+CELL"), ('underline'))
    # Recorrer cada fila y agregarla al objeto Text
    for row_key, row_data in table_data['rows'].items():
        for column_family, column_data in row_data.items():
            for qualifier, qualifier_data in column_data.items():
                column = f"{column_family}:{qualifier}"
                value = qualifier_data['value']
                timestamp = qualifier_data['timestamp']
                # Agregar la información de la celda a la columna COLUMN+CELL
                output.insert('end', "{:<20} {:<30}".format(row_key, f"column={column}, timestamp={timestamp}, value={value}\n"))
                
    # Estilo de texto en negrita y subrayado para la columna ROW
    output.tag_configure('underline', underline=True)

# get "employees", "Yong", { COLUMN => "personal_data:age", VERSIONS => 3 }
def get_table(table_name,row,columns):
    table_file = os.path.join(data_dir, f"{table_name}.json")

    # print(table_name)
    # print(row)
    # print(columns)

    if not os.path.exists(table_file):
        # print(f"Table '{table_name}' does not exist.")
        output.insert('end', f"Table '{table_name}' does not exist.")
        return
    
    with open(table_file, "r") as f:
        table_data = json.load(f)

    #revisa su estado si esta disable o enable
    if table_data["state"] == False:
        output.insert('end',f"Table '{table_name}' is disable.")
        return
    
    output.insert('end', "{:<20} {:<30}\n".format("ROW", "CELL"), ('underline'))
    if columns:
        key = []
        value = []
        for x in columns:
            key.append(x.split("=>")[0].replace('"','').replace("'", '').strip())
            value.append(x.split("=>")[1].replace('"','').replace("'", '').strip())
        # print("key: ", key)
        # print("value: ", value)
        if "COLUMN" in key:
            indice = key.index("COLUMN")
            data = value.pop(indice).split(":")
            #revisar si existe la columna
            if data[0] not in table_data["rows"][row]:
                output.insert('end', f"Data '{data[0]}' does not exist in table '{table_name}'.")
                return
            column = f"{data[0]}:{data[1]}"
            values = table_data['rows'][row][data[0]][data[1]]['value']
            timestamp = table_data['rows'][row][data[0]][data[1]]['timestamp']
            output.insert('end', "{:<20} {:<30}".format(column, f"timestamp={timestamp}, value={values}\n"))

        else:
            columnas = table_data['columns']
            for key_value, data_value in columnas.items():
                noExiste = False
                # print("key_value: ", key_value)
                # print("data_value: ",data_value)
                for l in range(len(key)):
                    # print(f"{key[l]} y {value[l]}")
                    if data_value[key[l]] == value[l]:
                        # print(f"{key[l]} == {value[l]}")
                        pass
                    else:
                        noExiste = True
                if noExiste:
                    # print(f'NO EXISTE para {key_value}')
                    pass
                else:
                    # Recorrer cada fila y agregarla al objeto Text
                    for row_key, row_data in table_data['rows'][row][key_value].items():
                        # print("row_key: ", row_key)
                        # print("row_data: ", row_data)
                        column = f"{key_value}:{row_key}"
                        valueAdd = row_data['value']
                        timestamp = row_data['timestamp']
                        # Agregar la información de la celda a la columna COLUMN+CELL
                        output.insert('end', "{:<20} {:<30}".format(column, f"timestamp={timestamp}, value={valueAdd}\n"))

    else:
        # print(table_data)
        #revisar que exista la columna que se esta buscando
        if row not in table_data["rows"]:
            output.insert('end', f"Data '{row}' does not exist in table '{table_name}'.")
            return
        
        # Recorrer cada fila y agregarla al objeto Text
        for row_key, row_data in table_data['rows'][row].items():
            # print("row_key: ", row_key)
            # print("row_data: ", row_data)
            for column_family, column_data in row_data.items():
                # print("column_family: ",column_family)
                # print("column_data: ", column_data)
                column = f"{row_key}:{column_family}"
                value = column_data['value']
                timestamp = column_data['timestamp']
                # Agregar la información de la celda a la columna COLUMN+CELL
                output.insert('end', "{:<20} {:<30}".format(column, f"timestamp={timestamp}, value={value}\n"))
            # print("============")
                
    # Estilo de texto en negrita y subrayado para la columna ROW
    output.tag_configure('underline', underline=True)
                


#generacion del interfaz y lectura de texto
root = tk.Tk()

# Crear un cuadro de texto
entry = tk.Entry(root, width=100)
entry.pack()

# Crear un botón de submit
submit_button = tk.Button(root, text="Submit", command=submit_text)
submit_button.pack()

# Crear un cuadro de texto para la salida
output = tk.Text(root, height=50, width=150)
# output = tk.Label(root, text="")
output.pack()

root.mainloop()

