from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, emit
from ttt import Field
from uuid import uuid4

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8564gdfz\n\xec]/'
socketio = SocketIO(app, logger=True)
fields = {}
rooms = {}
players = {}

@app.route("/")
def index():
    if 'id' not in session:
        session['id'] = uuid4().hex

    if session['id'] not in fields.keys():
        fields[session['id']] = Field()

    return render_template('index.html', field=fields[session['id']])

@app.route("/move")
def move():
    x = int(request.args.get('x', '-1'))
    y = int(request.args.get('y', '-1'))

    if 'id' not in session: return "Session not found", 400

    field = fields[session['id']]
    field.move(x, y)

    lines, who = field.check_win()

    if any(lines):
        print(who, lines)
        print(field)

        return  "<th>" +\
               f"<img src=\"{'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Red_X.svg/1200px-Red_X.svg.png' if field.get_cell(x, y) == 'X' else 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Deseret_capital_long_O.svg'}\">" +\
                '</th>', {"HX-Trigger-After-Swap": "moves, end_game"}
    else:
        return "<th>" +\
              f"<img src=\"{'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Red_X.svg/1200px-Red_X.svg.png' if field.get_cell(x, y) == 'X' else 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Deseret_capital_long_O.svg'}\">" +\
               '</th>', {"HX-Trigger-After-Swap": "moves"}

@app.route("/moves")
def moves():
    if 'id' not in session: return "Session not found", 400
    return render_template('moves.html', moves=", ".join(fields[session['id']].moves))

@app.route('/set_moves')
def set_moves():
    moves = request.args.get('moves', '')

    if 'id' not in session: return "Session not found", 400

    del fields[session['id']]
    fields[session['id']] = Field.set_moves(moves.upper())

    return render_template('field.html', field=fields[session['id']])


@app.route("/new-game")
def new_game():
    if session['id'] in fields.keys():
        del fields[session['id']]

    fields[session['id']] = Field()

    return render_template('index.html', field=fields[session['id']]), {'HX-Refresh': "true"}

@app.route("/create")
def create():
    if 'id' not in session: return "Session not found", 400

    room_id = uuid4().hex[-6:]
    fields[room_id] = Field()
    rooms[room_id] = {session['id']}
    players[session['id']] = True  # X

    return redirect(f"/room/{room_id}", code=302)


@app.route("/room/<room_id>")
def room(room_id):
    if 'id' not in session:       return "Session not found",   400
    if room_id not in fields:     return "Room does not exist", 400
    if 'room_id' not in session and \
        len(rooms[room_id]) == 2: return "Room is full",       400 
    else: session['room_id'] = room_id

    if session['id'] not in players: players[session['id']] = not players[list(rooms[room_id])[0]]

    print(players[session['id']])

    return render_template('multiplayer.html', field=fields[room_id], ID=room_id)

@socketio.on('HELO')
def handle_HELO(json):
    print(session.keys())
    print(json)

@socketio.on('MOVE')
def handle_MOVE(json):
    room_id = session['room_id']
    field = fields[room_id]
    mark = 'X' if players[session['id']] else 'O'
    print(mark, field.next)
    if (mark == field.next):
        field.move(json['x'], json['y'])
        emit('CHNG', {"room_id": session['room_id']}, broadcast=True)
    print(session.get('id'), session.get('room_id'))
    print('received json: ' + str(json))