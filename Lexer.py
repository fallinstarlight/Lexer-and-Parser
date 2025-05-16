import re

token = []

# Expresiones regulares para cada token, declaradas en un arreglo junto a su nombre de identificación
token_patterns = [
    # (pattern, token_name)
    (re.compile(r"\?.*"), "comentario"),
    (re.compile(r"(\bif\b|\bwhile\b|\bstart\b|\bend\b|\breturn\b|\breturns\b|\belse\b|\belif\b|\bchoose\b|\bcase\b|\brange\b|\bdefine\b|\bint|\bfloat\b|\bstring\b|\bbool\b)|\bprint\b"), "palabra_clave"),
    (re.compile(r"(\(|\)|;|\[|\]|\,)"), "delimiter"),
    (re.compile(r"(@|\$)[a-zA-Z]+[a-zA-Z0-9_]*\b"), "identificador"),
    (re.compile(r"\-[0-9]+\.[0-9]+"), "negativo_decimal"),
    (re.compile(r"[0-9]+\.[0-9]+"), "decimal"),
    (re.compile(r"\-[0-9]+"), "negativo"),
    (re.compile(r"([0-9]+|\+[0-9]+)"), "entero"),
    (re.compile(r"(\+\+|\-\-|=)"), "asgm_op"),
    (re.compile(r"[\+\*-\/]"), "arit_op"),
    (re.compile(r"(<>|><|<=|>=|==|<|>)"), "cmp_op"),
    (re.compile(r"(\band\b|\bor\b)"), "bool_op"),
    (re.compile(r"(\"|\').*(\"|\')"), "texto")
]

# Función para leer un archivo
def getfromfile(file_path): #requiere la ruta del archivo
    try:
        with open(file_path, 'r') as file:
            return file.read().split('\n') #separa el texto usando los saltos de línea (\n) y lo devuelve como arreglo 
    except FileNotFoundError:
        # manejo de excepciones al no encontrar el archivo o abrirlo
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

#función para el análisis léxico, recibe como parámetro el código dividido en líneas
def lexic_analyzer(code):
    """Perform lexical analysis on the code"""
    # definir los arreglos para la tabla de tokens y la lista de errores (lexemas no reconocidos)
    token_table = []
    errors = []
    
    # Esta expresión regular es especial, pues es para identificar la declaración de variables sin el @ al inicio y así mandar
    # un mensaje de error especial
    missing_at_regex = re.compile(r'^\b[a-zA-Z]+[a-zA-Z0-9_]*\b')
    
    # aquí empieza el análisis, se itera a través de cada línea del arreglo del código a analizar, se enumera cada línea
    for line_num, original_line in enumerate(code, 1):
        # la función strip se deshace de espacios al inicio y al final de la línea
        stripped_line = original_line.strip()
        # si a la línea no se le pudo aplicar strip, significa que es una línea en blanco y se salta completamente, empezando el
        # ciclo con una línea nueva
        if not stripped_line: 
            continue

        # se trabaja con la línea cortada, sin los espacios al inicio y al final
        current_line = stripped_line
        
        # se empieza a analizar la línea para encontrar coincidencias, se va analizando desde el inicio de la línea
        # se analizará la línea hasta agotarla
        while current_line:
            # si el primer caracter de la línea es un espacio, este se salta y se avanza al siguiente caracter
            if current_line[0].isspace():
                current_line = current_line[1:]
                continue
                
            # variable que nos dice si se encontró una coincidencia, se inicializa a falso porque aún no se ha encontrado nada
            matched = False
            
            """aquí se analiza token por token buscando una coincidencia
            pattern: expersión regular
            token_type: nombre del token
            token_patterns: tabla de expresiones regulares definida al inicio """

            for pattern, token_type in token_patterns:
                # función match de la librería re, busca el patrón de la expresión regular en la línea de código (current_line)
                match = pattern.match(current_line)
                if match:
                    # si se encuentra una coincidencia la variable match es puesta a true
                    matched = True
                    # se añade la coincidencia (value) a la tabla de tokens junto al nombre del token (token_type) y la línea de código
                    value = match.group()
                    token_table.append({
                        'line': line_num,
                        'type': token_type,
                        'value': value
                    })
                    # se remueve la parte del código que coincidió para no ser analizada de nuevo
                    current_line = current_line[match.end():]
                    # se sale del ciclo for pues ya se encontró una coincidencia
                    # se devuelve al inicio del ciclo while para seguir analizando la línea hasta agotarla
                    break
                # si no se encuentra una coincidencia, se continua con la siguiente expresión regular hasta agotarlas todas
                    
            # si no se encontró ninguna coincidencia
            if not matched:
                # encontrar el siguiente espacio o salto de línea para delimitar el lexema no reconocido
                next_space = len(current_line)
                for i, char in enumerate(current_line):
                    if char.isspace():
                        next_space = i
                        break
                
                # variable de error que almacena el lexema no reconocido
                error_part = current_line[:next_space]
                
                # Se analiza si el lexema luce como una variable sin el símbolo @ al inicio
                missing_at_match = missing_at_regex.match(error_part)
                if missing_at_match:
                    # de ser cierto entonces se crea el error con una corrección especial
                    suggested_correction = f"@{error_part}"
                    # los errores se añaden al arreglo de errores
                    errors.append({
                        'line': line_num,
                        'error': f"Unrecognized token: '{error_part}' - did you mean '{suggested_correction}'?"
                    })
                else:
                    # si no entonces se crea un mensaje de error genérico
                    errors.append({
                        'line': line_num,
                        'error': f"Unrecognized token: '{error_part}'"
                    })
                
                current_line = current_line[next_space:]
        # se continua analizando el texto aunque haya errores
                
    # se devuelve la tabla de errores o la tabla de tokens, sea el caso
    if errors:
        return {'errors': errors}
    else:
        return {'tokens': token_table}

if __name__ == "__main__":
    print("Performing lexic analysis")
    file_path = input("Enter the path to your code file: ").strip()
    code_to_compile = getfromfile(file_path)
    
    if not code_to_compile:
        print("No code to analyze.")
    else:
        result = lexic_analyzer(code_to_compile)
        if 'errors' in result:
            print("Your code contains the following errors:")
            for error in result['errors']:
                print(f"Line {error['line']}: {error['error']}")
        else:
            print("Here is your token table:")
            for token in result['tokens']:
                print(f"Line {token['line']}: {token['type']:20} -> {token['value']}")