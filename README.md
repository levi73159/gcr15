# Game Core Raw XV (GCR15)

## How it works
The language is a language design to accsess the file memory easily, 
it is design to be low level and easy to use

## How to set up
1. install python on your platform
2. install pyinstaller by using `pip install pyinstaller`
3. install gcr by using `python3 -m PyInstaller --onefile code/gcr.spec`
4. locate the exe in the dist folder
5. create a `[name].gcr` file
6. add any code you want see Commands Section
7. compile the program by using `gcr.exe compile --in_file [name].gcr --out_file out.bin`
8. run the program by using `gcr.exe run --file out.bin --entry_point 350`
9. or you can use the `CR (Compile and Run)` command

### Compiler Directives

#### Memory
**NOTE: Memory does not reset to normal when you run it**

- **`malc {values}`:** Allocates multiple integers (4 bytes) of memory; it can also allocate a string.
- **`malcb {values}`:** Allocates multiple bytes of memory; it can also allocate a string.
- **`malcs {size} {value}`:** Allocates a block of memory of the specified size and initializes each value with the provided initial value.
- **`org {location}`:** Moves the current file position to the specified location. This directive is crucial for controlling the position within the file where subsequent code or data will be written during compilation.

**NOTE: It is recommended that you add at least a 100 byte padding between the start, so you don't override the metadata at the start of the program**

#### Definition
- **`define {name} {definition}`:** Defines a variable that will be replaced with the specified value during compilation.

### Commands

#### Memory Operations
- **`set {location} {value | ptr}`:** Sets the value at the specified memory location to the given value. Note: When setting a byte using a pointer, it will automatically be formatted as an integer, so use `setb` for bytes.
- **`seti {location} {value | ptr}`:** Sets the value at the specified memory location to the given integer value (4 bytes).
- **`setb {location} {value | ptr}`:** Sets the value at the specified memory location to the given byte value.
- **`sets {location} {value | ptr}`:** Sets the value at the specified memory location to the given string.

#### Output
- **`print {string location/ptr}`:** Prints a string to the screen.
- **`printp {memory location/ptr}`:** Prints a byte from the specified memory location to the screen.
- **`printi {int location/ptr}`:** Prints an integer (4 bytes) from the specified memory location to the screen.
- **`printc {int}`:** Prints an integer as a character.
- **`print_cptr {memory location/ptr}`:** Prints a single byte as a character.

#### Jump
- **`jmp {location}`:** Jumps to the specified location.

### Labels/Pointers

Labels are a way to mark specific locations in your code, 
allowing you to refer to those locations easily using symbolic names. 
In GCR15, labels serve as pointers to memory locations, 
simplifying navigation and providing a higher level of abstraction.
They are essential for creating structured and readable code.

- **`{name}:`:** Defines a label with the specified name at the current code location.

- **`[label_name]`:** Represents a memory pointer to the location marked by the label with the specified `label_name`. When used in commands or expressions, `[label_name]` allows you to access the memory content at the labeled location.

Using square brackets `[...]` with a label name provides a convenient way to reference memory locations indirectly through labels. It adds a layer of abstraction, making the code more expressive and modular.
Labels act as placeholders for memory addresses, offering a more intuitive and human-readable representation of memory manipulation. They contribute to the clarity and organization of your code, making it easier to understand and maintain.

### Strings:
- **`"..."`:** Strings in double quotes represent a sequence of characters. These strings can be used as arguments in various commands, providing a way to handle and manipulate text data in the program.

Strings play a crucial role in storing and displaying textual information. They can be passed as arguments to commands like `sets`, enabling the manipulation and storage of strings in the allocated memory. The double quotes indicate the beginning and end of a string literal, allowing for easy identification in the code.
Strings ends in a 3 so when creating a string make sure to use the escape character `\3` to end the text

### Comments:
- **`;`** Comments in GCR15 are denoted by the semicolon (`;`) symbol. Anything following a semicolon on a line is treated as a comment and is ignored during compilation and execution. Comments are used for adding explanatory notes, annotations, or remarks within the code without affecting the program's functionality.

For example:
```
seti [number] 42  ; Set the value at number to 42 
```

In this case, the text after the semicolon is a comment and will be ignored by the GCR15 compiler and interpreter. Comments are useful for providing context or explanations for specific code segments.

### Examples:

#### **creating a string:**
```nasm
org 100
string: malc "Hello, world" 0xA 0x3
string2: malc "Hello, world\n\3"
```

#### **printing and looping:**
```
org 100
define END_STR 0xA 0x3
string: malc "Hello, world" END_STR ; the end_str will be replaced with 0xA and 0x3

loop:
print [string]
jmp [loop]
```

#### **setting program:**
```
org 100
define END_TEXT 3

string: malcb "hello, world\n" END_TEXT
string2: malcb "hello, not\n" END_TEXT
int: malc 1000

set [string] "hello, world\n\3"     ; setting string to normal
set [int] 1000                      ; setting int to normal
printi [int]                        ; printing
printc 0xA                          ; printing new line
set [int] 600                       ; setting int to 600
printi [int]                        ; printing new int
printc 0xA                          ; new line
print [string]                      ; printing string
set [string] [string2]              ; changing string
print [string]                      ; prinint new string
```