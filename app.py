from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from scraper import get_info
from gemini_api import get_report

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@socketio.on('generate_report')
def generate(data):
    code = data.get('code')
    print("code: ", code)
    if not code:
        emit('message', {
                'type': 'error',
                'text': 'Código de aeroporto inválido.'
            })
        return

    data_json = get_info(code.lower(), emit)
    if not data_json:
        emit('message', {
                'type': 'error',
                'text': 'Código de aeroporto inválido.'
            })
        return
    report = get_report(data_json, emit)
    emit('message', {
            'type': 'alert',
            'text': 'Relatório pronto!'
        })

    emit('message', {
            'type': 'success',
            'text': report
        })

if __name__ == '__main__':
    socketio.run(app, debug=True)