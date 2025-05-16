**Luna Hidalgo Francisco Emmanuel**
**Ingeniería en sistemas computacionaeles**
**Instituto tecnológico de Pachuca**
**Lenguajes y Autómatas I**

**Analizador Léxico y Sintáctico**

Este es un pequeño y sencillo proyecto de excuela que busca implementar un analizador léxico y sintáctico que lea un código en un pseudolenguaje inventado y arroje una tabla de tokens
así como valide la estructura del mismo, asegurándose que todo el código siga una gramáticca correcta.

**Analizador Léxico**

> Separa el código fuente en líneas
> Lee caracter por caracter
> Se vale de expresiones regulares para detectar tokens
> Almacena los tokens, su posición y su valor
> Si encuentra errores los notifica y detiene el análisis
> Si todo es correcto, genera una tabla de tokens

**Analizador Sintáctico**

> Itera a través de la tabla de tokens
> Usa un análisis descendente
> Al identificar un token se dirige a la definición de dicho token
> Esta definición representa una gramática que detecta que el token sea sucedido por los tokens correctos
> Si encuentra un token inválido notifica y detiene el análisis
> Da una pequeña retroalimentación para saber dónde y cuál fue el error

**Notas**

Ambos analizadores son muy básicos y trabajan con conjuntos muy pequeños de patrones, no esperen encontrar un nuevo lenguaje de programación.
Aún no cuenta con análisis de semántica, por lo que, a ojos de este analizador, if(10 == true) o int -10.291; son líneas perfectamente válidas.
Aún presenta dificultad con expresiones aritméticas que presenten múltiples paréntesis anidados: 
> a + b ✓

> (a + b) ✓

> (a) + (b) ✓

> (((a + b))) ✓

> a + (b) ✓

> (a + (b)) ✗

**Símbolos válidos**

Lista de los tokens que cree, que indican básicamente las reglas del lenguaje y qué cadenas de texto son válidas:
Palabras reservadas:

if, while, define, return, returns, else, elif, choose, range, int, float, string, bool, case, print

Operadores

+ - * / ^ < > <> >< and or ++ -- =

Delimitadores

; ( ) start end : ,

Identificadores

@ $

Números

Cualquier número

Texto

Cualquier texto entre comillas "" ''

