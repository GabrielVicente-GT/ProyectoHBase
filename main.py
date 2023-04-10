import tkinter as tk
import json

#create "employees", "personal_data", "profesional_data"
#put "employees", "Geoffrey", "personal_data:age", 32

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
    
        add_row(table_name, row_key, column, value, new_value)
        output.config(text = f'Row added to table "{table_name}" with row_key {row_key} and column {column} added it variable {new_value} set to {value}\n')
        
    else:
        output.config(text="Comando no reconocido")

# Función para crear la tabla
def create_table(table_name, columns):
    table = {"row_key": []}
    for column in columns:
        table[column] = []
    with open(f'{table_name}.json', 'w') as f:
        json.dump(table, f)
    print(f'Table {table_name} created with columns: {columns}')
    # table = {1: {col: '' for col in columns}}
    # # Eliminar las comillas del nombre de la tabla
    # table_name = table_name.replace('"', '')
    # with open(f'{table_name}.json', 'w') as f:
    #     json.dump(table, f)

#funcion del put
def add_row(table_name, row_key, column, value, new_value):
    # Cargar el archivo JSON de la tabla correspondiente.
    with open(f'{table_name}.json', 'r') as f:
        table = json.load(f)

    # Buscar si la row_key ya existe en el archivo JSON.
    if row_key in table['row_key']:
        # Buscar si la columna ya existe en el archivo JSON.
        if column in table:
            # Actualizar el valor de la new_value en el archivo JSON.
            table[column][table['row_key'].index(row_key)] = new_value
        else:
            # Crear una nueva columna y agregar el valor de new_value.
            table[column] = ['' for _ in range(len(table['row_key']))]
            table[column][table['row_key'].index(row_key)] = new_value
    else:
        # Crear una nueva fila y agregar la row_key y la columna con el valor de new_value.
        table['row_key'].append(row_key)
        for key in table.keys():
            if key != 'row_key':
                table[key].append('')
        table[column][table['row_key'].index(row_key)] = new_value

    # Guardar el archivo JSON modificado.
    with open(f'{table_name}.json', 'w') as f:
        json.dump(table, f)
        
    output.config(text=f'Added value {value} to row key {row_key} and column {column} in table {table_name}. {column} is now set to {new_value}')






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

