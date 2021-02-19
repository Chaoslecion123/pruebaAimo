# Run with "python client.py"
from bottle import get, run, static_file

@get('/')
def index():
    return static_file('./templates/index.html', root=".")

@get('/listar_notas')
def list_notas():
    return static_file('./templates/lista_notas.html', root=".")

@get('/crear_nota')
def list_notas():
    return static_file('./templates/crear_nota.html', root=".")

run(host='localhost', port=5000,reloader= True, debug=True)
