import tkinter as tk
import json
import os
import time

#create "employees", "personal_data", "profesional_data"
#put "employees", "Geoffrey", "personal_data:age", 32
#alter "employees", { NAME => "profesional_data", VERSIONS => 3 
# InsertMany 'employees', 'Tomas', 'personal_data:age', 15 , 'Yong', 'personal_data:age', 18, 'Yong', 'profesional_data:position', 'intern'

data_dir = "data"

def submit_text():
    clear_output_text()
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
    #command de putMany
    elif command.startswith('InsertMany'):
        print(command_parts)
        table_name = command_parts[0].replace('InsertMany', '').replace('"', '').replace("'", '').strip()
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

        print("table_name: ", table_name)
        print("row_key: ", array_row_key)
        print("column: ", array_column)
        print("value: ", array_value)
        
        if rowKeyLen == columLen == valueLen:
            for l in range(rowKeyLen):
                put_data(table_name,array_row_key[l],array_column[l],array_value[l])
            

        else:
            output.insert('end',f'Error, falta algun argumento')

        
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
        
    #scan command
    elif command.startswith("scan"):
        table_name = command.replace("scan", '').replace('"','').replace("'", '').strip()
        scan_table(table_name)
        
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

