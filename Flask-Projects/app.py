from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

ALLOWED_ROOMS = {"naveenkanna"}
chat_history = defaultdict(list)
room_users = defaultdict(set)

@app.route('/', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        if room in ALLOWED_ROOMS:
            session['username'] = username
            session['room'] = room
            return redirect(url_for('chat'))
        else:
            return render_template('join.html', error="Invalid room key.")
    return render_template('join.html')

@app.route('/chat')
def chat():
    if 'username' not in session or 'room' not in session:
        return redirect(url_for('join'))
    room = session['room']
    return render_template('chat.html', username=session['username'], room=room, chat_history=chat_history[room])

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    room = session.get('room')
    if username and room:
        join_room(room)
        if username not in room_users[room]:
            room_users[room].add(username)
        for msg in chat_history[room]:
            emit('message', {'msg': msg}, room=request.sid)
        emit('message', {'msg':   f"{username} has joined the chat."}, room=room, include_self=False)

@socketio.on('message')
def handle_message(data):
    msg = f"{data['username']}: {data['msg']}"
    chat_history[data['room']].append(msg)
    emit('message', {'msg':    msg}, room=data['room'], broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('typing', {'username': data['username']}, room=data['room'], include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    emit('stop_typing', {'username': data['username']}, room=data['room'], include_self=False)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    if username in room_users[room]:
        room_users[room].remove(username)
    leave_room(room)
    emit('message', {'msg':  f"{username} has left the chat."}, room=room, render_template='join.html')

if __name__ == '__main__':
    socketio.run(app, port=5000,  debug=True)
    
