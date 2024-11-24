### Variable names:
Snake case, e.g. :
  - hello
  - hello_world

CAPS for constant, e.g. :
  - CONST
  - THIS_IS_A_CONST

### Comments:
Optional

### Write testable functions:
<pre>Testable functions are typically small, focused on a single responsibility, and have clear inputs and outputs. They avoid side effects, such as modifying global variables or relying on external states. The goal is to write functions that can be tested in isolation.</pre>

### Project structure:
  - database/ : Store .json database files
  - src/ : Store .py source files for the program
    - __init\__.py is the entry point of the porject
    - Create new files if required in this directory  
  - tests/ : Store .py unit test files

### git push
Run
<pre>poetry run format</pre>
and
<pre>poetry run lint</pre>
before running git push