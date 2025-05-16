import re

token = []

# Expresiones regulares para cada token, declaradas en un arreglo junto a su nombre de identificación
token_patterns = [
    # (pattern, token_name)
    (re.compile(r"\?.*"), "comentario"),
    (re.compile(r"(\bif\b|\bwhile\b|\bstart\b|\bend\b|\breturn\b|\breturns\b|\belse\b|\belif\b|\bchoose\b|\bcase\b|\brange\b|\bdefine\b|\bint|\bfloat\b|\bstring\b|\bbool\b|\bvoid\b|\bprint\b|\btrue\b|\bfalse\b)"), "palabra_clave"),
    (re.compile(r"(:|\(|\)|;|\[|\]|\,)"), "delimiter"),
    (re.compile(r"(@|\$)[a-zA-Z]+[a-zA-Z0-9_]*\b"), "identificador"),
    (re.compile(r"\-[0-9]+\.[0-9]+"), "negativo_decimal"),
    (re.compile(r"[0-9]+\.[0-9]+"), "decimal"),
    (re.compile(r"\-[0-9]+"), "negativo"),
    (re.compile(r"([0-9]+|\+[0-9]+)"), "entero"),
    (re.compile(r"(\+\+|\-\-|=)"), "asgm_op"),
    (re.compile(r"[\+\*-\/\^]"), "arit_op"),
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

# Clase parser, encargada del análisis sintáctico
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.errors = []
        self.advance()

    # función para iterar entre los tokens de la tabla de tokens
    def advance(self):
        # empezamos desde la primera fila
        self.token_index += 1
        # revismanos que nos encontremos dentro de la matriz de tokens 
        # asignamos a la variable self.current_token el valor que estamos leyendo actualmente, o ninguno si es que ya hemos acabado
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None
        return self.current_token

    # función para leer el token siguiente
    def peek(self):
        peek_index = self.token_index + 1
        if peek_index < len(self.tokens):
            return self.tokens[peek_index]
        return None

    # función para saber si el token analizado es igual al patrón con el que se le compara
    def match(self, expected_type, expected_value=None):
        # sil el tipo de token es igual al esperado y el valor del token es igual al valor esperado devolver el token en cuestión y avanzar al siguiente token
        if self.current_token and self.current_token['type'] == expected_type:
            # a veces no se espera un valor específico, sólo un tipo de tokens, pues pueden tomar cualquier valor (p. ej. variables o números)
            if expected_value is None or self.current_token['value'] == expected_value:
                token = self.current_token
                self.advance()
                return token
        # devolver nulo si no se haya una coincidencia
        return None

    # función para reportar errores al usuario, junto a la línea en la que se encuentra dicho error
    def error(self, message):
        line = self.current_token['line'] if self.current_token else 'unknown'
        self.errors.append(f"Syntax error at line {line}: {message}")
        return False

    # función principal, itera a través de los tokens
    def parse(self):
        """Main parsing method"""
        while self.current_token:
            # ignora comentarios
            if self.current_token['type'] == 'comentario':
                self.advance()
                continue
            # si la función statement retorna falso (encuentra una línea de código no válida), retorna falso
            if not self.statement():
                return False
        # retorna verdadero si no hay errores
        return len(self.errors) == 0

    # analiza las líneas de código para ver si son válidas, si la línea de código sigue un patrón esperado, retorna verdadero, si no, falso
    def statement(self):    
        """Parse a statement"""

        # ignora comentarios
        while self.current_token and self.current_token['type'] == 'comentario':
                self.advance()
                # si el código sólo contiene comentarios, termina la ejecución
                if not self.current_token:
                    return True
                
        # para leer variables, si encuentra un tipo de dato y adelante hay una variable, identifica una declaración de variable
        next_token = self.peek()
        if (self.current_token['type'] == 'palabra_clave' and 
            self.current_token['value'] in ('int', 'float', 'string', 'bool')):
            if next_token and next_token['type'] == 'identificador':
                return self.variable_declaration()
            else:
                self.error("Expected variable after identifier")
        
        
        # análisis de patrones, si encuentra alguna de las palabras reservadas en el código, llamará a la función correspondiente, dicha función se encargará
        # de validar que después de dicha palabra clave se encuentre una estructura de código válida
        # si estas funciones validan el token, harán que la función statement retorne verdadero, si no, retornará falso
        # si no coincide con una palabra, seguirá a la siguiente hasta agotarlas todas 
        # si agota todas las palabras clave o posibles expresiones de código, la función statement() retornará false, pues no hubo match con nada
        if self.match('palabra_clave', 'define'):
            return self.function_declaration()
        if self.match('palabra_clave', 'if'):
            return self.if_statement()
        if self.match('palabra_clave', 'while'):
            return self.while_statement()
        if self.match('palabra_clave', 'range'):
            return self.range_statement()
        if self.match('palabra_clave', 'choose'):
            return self.choose_statement()
        if self.match('palabra_clave', 'else'):
            return self.else_statement()
        if self.match('palabra_clave', 'print'):
            return self.print_statement()
        if self.match('palabra_clave', 'return'):
            return self.return_statement()
        
        # Funciona de forma parecida a lo de arriba, pero en lugar de palabras clave busca expresiones matemáticas o uso de variables
        return self.expression_statement()

    """
    Todas estas son las funciones específicas que son llamadas dependiendo del patrón que se ecnuentre en el token
    Por ejemplo, si el token analizado es la palabra if, el programa llamará a la función if_statement() la cual validará que la estructura que sigue a dicho if sea
    correcta.
    Todas las funciones retornan un verdadero o un falso, porque como ya se mencionó, la función statement (que es de donde se llama a estas otras funciones) devuelve
    verdadero o falso dependiendo de si se encuentra un patrón definido

    """
    # analiza la estructura de una declaración de variables
    def variable_declaration(self):
        """Parse variable declaration"""
        self.advance()  # Consume the type
        
        if not self.match('identificador'):
            return self.error("Expected variable name after type")
        if self.expression():
           return self.error("Expected = before assingment") 
        
        # Optional initialization
        if self.match('asgm_op', '='):
            if not (self.expression() or self.match('texto')):
                return self.error("Expected expression or string after '='")
        
        if not self.match('delimiter', ';'):
            return self.error("Expected ';' after declaration")
        
        return True

    # analiza la estructura de una expresión que use variables (para evitar que el programa mande error si se está usando una variable ya declarada y por lo tanto
    # no lleva un tipo de dato)
    def expression_statement(self):
        """Handle expressions that might include variable usage"""
        # Allow already-declared variables here
        if self.match('identificador'):
            # Could be assignment or usage
            if self.match('asgm_op'):  # =, +=, etc.
                if not self.expression():
                    return self.error("Expected expression after assignment")
                if not self.match('delimiter', ';'):
                    return self.error("Expected ';' after statement")
            # Else it's just a variable usage
            
            return True
    
        return self.expression()

    # analiza la estructura de una declaración de función
    def function_declaration(self):
        """Parse function declaration"""
        if not self.match('identificador'):
            return self.error("Expected function name after 'define'")
        if not self.match('palabra_clave', 'returns'):
            return self.error("Expected 'returns' in function declaration")
        if not (self.match('palabra_clave', 'int') or self.match('palabra_clave', 'float') or
               self.match('palabra_clave', 'string') or self.match('palabra_clave', 'bool') or self.match('palabra_clave', 'void')):
            return self.error("Expected return type after 'returns'")
        if not self.match('delimiter', '('):
            return self.error("Expected '(' for parameters")
        
        # Parameters

        if not self.match('delimiter', ')'):  # Check if parameter list is not empty
            while True:
                # Parse parameter type
                if not (self.match('palabra_clave', 'int') or 
                    self.match('palabra_clave', 'float') or
                    self.match('palabra_clave', 'string') or 
                    self.match('palabra_clave', 'bool')):
                    return self.error("Expected parameter type")
                
                # Parse parameter name
                if not self.match('identificador'):
                    return self.error("Expected parameter name")
                
                # Check for closing parenthesis or comma
                if self.match('delimiter', ')'):
                    break  # End of parameters
                if not self.match('delimiter', ','):
                    return self.error("Expected ',' or ')' after parameter")
    
        # After parameter list
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' before function body")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for function body")
            
        # Function body
        while not self.match('palabra_clave', 'end'):
            if not self.statement():
                return False
        
        return True

    # analiza la estructura de un bloque condicional if
    def if_statement(self):
        """Parse if statement"""
        if not self.match('delimiter', '('):
            return self.error("Expected '(' after 'if'")
        if not self.condition():
            return False
        if not self.match('delimiter', ')'):
            return self.error("Expected ')' after condition")
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after condition")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for if body")
        
        # If body
        while not self.match('palabra_clave', 'end'):
            if not self.statement():
                return False
        
        # Optional elif/else
        while self.match('palabra_clave', 'elif'):
            if not self.elif_statement():
                return False
        
        if self.match('palabra_clave', 'else'):
            if not self.else_statement():
                return False
        
        return True

    # analiza la estructura de un bloque condicional elif
    def elif_statement(self):
        """Parse elif statement"""
        if not self.match('delimiter', '('):
            return self.error("Expected '(' after 'elif'")
        if not self.condition():
            return False
        if not self.match('delimiter', ')'):
            return self.error("Expected ')' after condition")
        
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after condition")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for elif body")
        
        while not self.match('palabra_clave', 'end'):
            if not self.statement():
                return False
        
        while self.match('palabra_clave', 'elif'):
            if not self.elif_statement():
                return False
        
        if self.match('palabra_clave', 'else'):
            if not self.else_statement():
                return False
        
        return True

    # analiza la estructura de un ciclo while
    def while_statement(self):
        """Parse while statement"""
        if not self.match('delimiter', '('):
            return self.error("Expected '(' after 'while'")
        if not self.condition():
            return False
        if not self.match('delimiter', ')'):
            return self.error("Expected ')' after condition")
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after condition")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for while body")
        
        while not self.match('palabra_clave', 'end'):
            if not self.statement():
                return False
            
        return True
    
    # analiza la estructura de un ciclo range
    def range_statement(self):
        """Parse range statement"""
        if not self.match('delimiter', '('):
            return self.error("Expected '(' after 'range'")
        
        if not (self.match('entero') or self.match('decimal') or 
                    self.match('negativo') or self.match('negativo_decimal') or
                    self.match('identificador') or self.expression()):
            return self.error("Expected start value")
        
        if not self.match('delimiter', ','):
            return self.error("Expected comma")
        
        if not (self.match('entero') or self.match('decimal') or 
                    self.match('negativo') or self.match('negativo_decimal') or
                    self.match('identificador') or self.expression()):
            return self.error("Expected end value")
        
        if not self.match('delimiter', ','):
            return self.error("Expected comma")

        if not (self.match('entero') or self.match('decimal') or 
                    self.match('negativo') or self.match('negativo_decimal') or
                    self.match('identificador') or self.expression()):
            return self.error("Expected step value")

        if not self.match('delimiter', ')'):
            return self.error("Expected ')'")
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after ´)")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for range body")
        
        while not self.match('palabra_clave', 'end'):
            if not self.statement():
                return False
            
        return True

    # analiza la estructura de una instrucción print
    def print_statement(self):
        """Parse print statement"""
        if not self.match('delimiter', '('):
            return self.error("Expected '(' after 'print'")
        
        if not (self.match('texto') or self.match('entero') or self.match('decimal') or \
                self.match('negativo') or self.match('negativo_decimal') or \
                self.match('identificador') or self.expression() or self.match('palabra_clave', 'true') or self.match('palabra_clave', 'false')):
                return self.error("Missing text to print")
        
        if not self.match('delimiter', ')'):
            return self.error("Expected ')")
        
        if not self.match('delimiter', ';'):
            return self.error("Missing ;")
        
        return True

    # analiza la estructura de una condición (usado por algunos bloques condicionales)
    def condition(self):
        """Parse a condition"""
        
        if not (self.expression() or self.match('palabra_clave', 'true') or self.match('palabra_clave', 'false')):
            return False
        
        op = self.match('cmp_op') or self.match('bool_op')
        if not op:
            return True  # Single expression is valid condition
        
        if not (self.expression() or self.match('palabra_clave', 'true') or self.match('palabra_clave', 'false')):
            return self.error("Expected expression after operator")
        
        if self.match('cmp_op') or self.match('bool_op'):
            if not self.condition():
                return  False
        
        return True

    # analiza la estructura de un bloque choose
    def choose_statement(self):
        """Parse choose statement with proper case handling"""
        if not self.match('delimiter', '('):
            return self.error("Expected '(' after 'choose'")
        if not self.match('identificador'):
            return self.error("Expected a variable inside choose statement")
        if not self.match('delimiter', ')'):
            return self.error("Expected ')' after variable")
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after choose clause")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for choose body")

        # Parse case statements until we hit 'end'
        while True:
            # Check for closing 'end' first
            if self.match('palabra_clave', 'end'):
                return True
            
            # Check for unexpected EOF
            if not self.current_token:
                return self.error("Missing 'end' for choose statement")
            
            # Require 'case' keyword
            if not self.match('palabra_clave', 'case'):
                return self.error("Expected 'case' or 'end' in choose block")
            
            # Parse the case statement
            if not self.case_statement():
                return False

    # analiza la estructura de un bloque else
    def else_statement(self):       
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after else")
        if not self.match('palabra_clave', 'start'):
            return self.error("Expected 'start' for else body")
        
        while not self.match('palabra_clave', 'end'):
            if not self.statement():
                return False
            
        return True

    # analiza la estructura de un bloque condicional case
    def case_statement(self):
        """Parse case statement with proper value and body handling"""
        # Parse case value (identifier, literal, or expression)
        if not (self.match('identificador') or 
                self.match('texto') or 
                self.match('entero') or 
                self.match('negativo') or 
                self.match('decimal') or 
                self.match('negativo_decimal') or 
                self.match('palabra_clave', 'true') or 
                self.match('palabra_clave', 'false') or
                self.expression()):
            return self.error("Expected value after 'case'")

        # Require colon after case value
        if not self.match('delimiter', ':'):
            return self.error("Expected ':' after case value")

        # Parse case body statements until next case or end
        while True:
            # Check for next case or end of choose
            if (self.current_token and 
                self.current_token['type'] == 'palabra_clave' and
                self.current_token['value'] in ('case', 'end')):
                return True
            
            # Parse regular statements
            if not self.statement():
                return False

    # analiza la estructura de una instrucción return
    def return_statement(self):
        if not (self.match('identificador') or self.expression() or self.match('texto') or self.match('entero') or \
                self.match('negativo') or self.match('decimal') or self.match('negativo_decimal') or self.match('palabra_clave', 'true') or \
                self.match('palabra_clave', 'false')):
                 return self.error("Expected variable, number, string or expression after 'return'")
        if not self.match('delimiter', ';'):
            return self.error("Missing ;")
        
        return True

    # analiza la estructura de expresiones aritméticas
    
    def expression(self):
        if self.match('delimiter', '('):
            if not self.expression():
                return False
            if not self.match('delimiter', ')'):
                return self.error("Missing closing parenthesis") 
            if self.match('arit_op'):   
                if not self.expression():
                    return False    
            return True
        
        if not (self.match('entero') or self.match('decimal') or 
                    self.match('negativo') or self.match('negativo_decimal') or
                    self.match('identificador')):
                return False
        
        if self.match('arit_op'):
            if not self.expression():
                return self.error("Expected valid expression after operator")
            return True

        if (self.expression()):
                return self.error("Mssing operator between numbers")

        return True
    
    
    

# Ejecución primaria
if __name__ == "__main__":
    while True:  #Permite ejecutar todo una y otra vez sin volver a iniciar el programa
        print("\n" + "="*50)
        print("Language Processor - Enter file path or 'exit' to quit")
        print("="*50)
        
        file_path = input("\nEnter the path to your code file: ").strip()
        
        # Para que el usuario indique si quiere salir del programa
        if file_path.lower() == 'exit':
            print("Exiting program...")
            break
        
        # Lee el archivo a analizar y lo prepara para el análisis léxico
        code_to_compile = getfromfile(file_path)
        if not code_to_compile:
            print("No code to analyze or file not found.")
            continue
        
        # ANÁLISIS LÉXICO
        # El lexer analiza el código
        lex_result = lexic_analyzer(code_to_compile)
        
        # si hay errores los muestra y ya no continua con la ejecución del lexer ni del parse
        if 'errors' in lex_result:
            print("\nLexical errors found:")
            for error in lex_result['errors']:
                print(f"Line {error['line']}: {error['error']}")
            continue  # Volver a inicio si encuentra errores
        
        # si no hay errores imprime la tabla de tokens
        print("\nToken table:")
        for token in lex_result['tokens']:
            print(f"Line {token['line']}: {token['type']:20} -> {token['value']}")
        
        # ANÁLISIS SINTÁCTICO
        print("\nStarting syntax analysis...")
        # crea objeto de tipo parser y lo inicializa con la tabla de tokens obtenida del lexer
        parser = Parser(lex_result['tokens'])

        # si la función parse() retorna verdadero, significa que no se encontró error alguno en el código
        if parser.parse():
            print("Syntax analysis completed successfully, no errors found")
        else:
            # de lo contrario, muestra el error sintático que se encontró y que provocó el abortaje del programa
            print("\nSyntax errors found:")
            for error in parser.errors:
                print(error)
        
        continues = input("\nPress enter to continue ")
    