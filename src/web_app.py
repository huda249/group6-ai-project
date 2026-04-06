import os
import sys
from flask import Flask, Response, jsonify, request, session

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from board import Board
from player import AIPlayer, HumanPlayer

app = Flask(__name__)
app.secret_key = "sofe3720-secret-key"

class _GameView:
    def __init__(self, board):
        self.board = board


def _players_and_start(mode, human_letter=None):
    if mode == 1: 
        hl = (human_letter or "X").upper()
        ai_letter = "O" if hl == "X" else "X"
        players = [HumanPlayer(hl), AIPlayer(ai_letter)]
        # If human chose O, AI is X and goes first
        start = 1 if hl == "O" else 0
        return players, start
    elif mode == 2:
        return [AIPlayer("X"), AIPlayer("O")], 0
    else:
        return [HumanPlayer("X"), HumanPlayer("O")], 0

def _load_board():
    b = Board()
    if "grid" in session:
        b.grid = [row[:] for row in session["grid"]]
    return b

def _save_board(board):
    session["grid"] = [row[:] for row in board.grid]

def _state():
    board = _load_board()
    winner = board.check_winner()
    done = winner is not None
    mode = session.get("mode")
    phase = session.get("phase", "setup")
    
    cur_idx = session.get("current_player_index", 0)
    cur_letter = None
    human_turn = False
    need_ai_step = False

    if mode and phase == "playing" and not done:
        hl = session.get("human_letter", "X")
        players, _ = _players_and_start(mode, hl)
        cur = players[cur_idx]
        cur_letter = cur.letter
        human_turn = isinstance(cur, HumanPlayer)
        need_ai_step = isinstance(cur, AIPlayer) and mode == 2

    return {
        "phase": phase,
        "mode": mode,
        "board": board.grid,
        "winner": winner,
        "done": done,
        "current_letter": cur_letter,
        "human_turn": human_turn,
        "need_ai_step": need_ai_step,
    }


INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Tic Tac Toe</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=JetBrains+Mono:wght@400;700&display=swap');

        :root {
            --teal-main: #008080;
            --teal-bright: #00f2f2;
            --teal-dark: #004d4d;
            --bg-dark: #0a0a0a;
            --card-bg: #141414;
            --text-light: #e0f2f2;
        }

        body {
            font-family: 'JetBrains Mono', monospace;
            background-color: var(--bg-dark);
            color: var(--text-light);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            text-transform: uppercase;
        }

        h1 {
            font-family: 'Syncopate', sans-serif;
            font-size: 1.8rem;
            letter-spacing: 4px;
            color: var(--teal-bright);
            margin-bottom: 2rem;
            text-shadow: 0 0 10px rgba(0, 242, 242, 0.3);
        }

        #setup, #play {
            background: var(--card-bg);
            padding: 1.5rem;
            border: 2px solid var(--teal-main);
            width: 100%;
            max-width: 320px;
            box-shadow: 8px 8px 0px var(--teal-dark);
        }

        fieldset {
            border: 1px solid var(--teal-dark);
            margin-bottom: 1rem;
            padding: 0.8rem;
            text-align: left;
        }

        legend { color: var(--teal-bright); font-weight: bold; padding: 0 5px; font-size: 0.7rem; }

        label { display: block; font-size: 0.7rem; margin: 8px 0; cursor: pointer; }

        button {
            width: 100%;
            padding: 0.8rem;
            background: transparent;
            border: 2px solid var(--teal-main);
            color: var(--teal-bright);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }

        button:hover:not(:disabled) {
            background: var(--teal-main);
            color: var(--bg-dark);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            margin: 1.5rem 0;
            border: 2px solid var(--teal-dark);
            width: 240px;
            margin-left: auto;
            margin-right: auto;
        }

        .cell {
            width: 80px;
            height: 80px;
            font-size: 2rem;
            font-family: 'Syncopate', sans-serif;
            background: var(--card-bg);
            border: 1px solid var(--teal-dark);
            color: var(--teal-bright);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        #status {
            font-size: 0.8rem;
            color: var(--teal-bright);
            margin-bottom: 1rem;
            border-left: 3px solid var(--teal-bright);
            padding-left: 10px;
            text-align: left;
            min-height: 1.2rem;
        }

        .hidden { display: none; }
        .row { margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Tic Tac Toe</h1>

    <div id="setup">
        <fieldset>
            <legend>Mode</legend>
            <label><input type="radio" name="mode" value="1" checked onchange="toggleXO()"> Human vs AI</label>
            <label><input type="radio" name="mode" value="2" onchange="toggleXO()"> AI vs AI (demo)</label>
            <label><input type="radio" name="mode" value="3" onchange="toggleXO()"> Human vs Human</label>
        </fieldset>

        <fieldset id="xoPick">
            <legend>Play as</legend>
            <label><input type="radio" name="hl" value="X" checked> X (Goes First)</label>
            <label><input type="radio" name="hl" value="O"> O (AI Goes First)</label>
        </fieldset>

        <button id="start">Start game</button>
    </div>

    <div id="play" class="hidden">
        <div id="status"></div>
        <div class="grid" id="board"></div>
        <button id="aiStep" class="hidden">AI move</button>
        <div class="row">
            <button id="newGame">New game</button>
        </div>
    </div>

    <script>
        function toggleXO() {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const xoField = document.getElementById('xoPick');
            // Only show X/O choice for Human vs AI
            xoField.classList.toggle('hidden', mode !== "1");
        }

        async function api(path, method='GET', body=null) {
            const opts = { method, headers: {'Content-Type': 'application/json'}};
            if (body) opts.body = JSON.stringify(body);
            const r = await fetch(path, opts);
            return r.json();
        }

        function render(s) {
            const setup = document.getElementById('setup');
            const play = document.getElementById('play');
            const boardEl = document.getElementById('board');
            const status = document.getElementById('status');

            if (s.phase === 'setup') {
                setup.classList.remove('hidden');
                play.classList.add('hidden');
                toggleXO();
                return;
            }

            setup.classList.add('hidden');
            play.classList.remove('hidden');
            boardEl.innerHTML = '';

            s.board.forEach((row, rIdx) => {
                row.forEach((cell, cIdx) => {
                    const btn = document.createElement('button');
                    btn.className = 'cell';
                    btn.textContent = cell === ' ' ? '' : cell;
                    if (s.human_turn && !s.done && cell === ' ') {
                        btn.onclick = () => move(rIdx, cIdx);
                    } else {
                        btn.disabled = true;
                    }
                    boardEl.appendChild(btn);
                });
            });

            document.getElementById('aiStep').classList.toggle('hidden', !s.need_ai_step || s.done);
            
            if (s.done) {
                status.textContent = s.winner === 'Draw' ? "It's a draw." : s.winner + " wins.";
            } else {
                status.textContent = s.current_letter + "'s turn.";
            }
        }

        async function move(r, c) { render(await api('/api/move', 'POST', {row: r, col: c})); }
        
        document.getElementById('start').onclick = async () => {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const hl = document.querySelector('input[name="hl"]:checked').value;
            render(await api('/api/configure', 'POST', {mode: mode, human_letter: hl}));
        };

        document.getElementById('aiStep').onclick = async () => render(await api('/api/ai_step', 'POST'));
        document.getElementById('newGame').onclick = async () => render(await api('/api/reset', 'POST'));

        (async () => render(await api('/api/state')))();
    </script>
</body>
</html>
"""


@app.route("/")
def index(): return Response(INDEX_HTML, mimetype="text/html")

@app.route("/api/state")
def get_state(): return jsonify(_state())

@app.route("/api/configure", methods=["POST"])
def configure():
    data = request.json
    mode = int(data['mode'])
    hl = data.get('human_letter', 'X')
    
    session.update({
        "mode": mode, 
        "phase": "playing", 
        "human_letter": hl,
        "current_player_index": 0
    })
    
    board = Board()
    _save_board(board)
    
    players, start = _players_and_start(mode, hl)
    session["current_player_index"] = start
    
    # If it's Human vs AI and the first player is the AI (happens if human picks O)
    if mode == 1 and isinstance(players[start], AIPlayer):
        row, col = players[start].get_move(_GameView(board))
        board.make_move(row, col, players[start].letter)
        _save_board(board)
        session["current_player_index"] = 1 - start

    return jsonify(_state())

@app.route("/api/move", methods=["POST"])
def move():
    data = request.json
    board = _load_board()
    mode = session.get('mode')
    hl = session.get('human_letter', 'X')
    idx = session.get('current_player_index')
    
    players, _ = _players_and_start(mode, hl)
    
    if board.make_move(data['row'], data['col'], players[idx].letter):
        session['current_player_index'] = 1 - idx
        _save_board(board)
        
        # If playing against AI, trigger AI move immediately
        if mode == 1 and not board.check_winner():
            players_updated, _ = _players_and_start(mode, hl)
            new_idx = session['current_player_index']
            ai_move = players_updated[new_idx].get_move(_GameView(board))
            board.make_move(ai_move[0], ai_move[1], players_updated[new_idx].letter)
            _save_board(board)
            session['current_player_index'] = 1 - new_idx
            
    return jsonify(_state())

@app.route("/api/ai_step", methods=["POST"])
def ai_step():
    board = _load_board()
    idx = session.get('current_player_index')
    players, _ = _players_and_start(2) # AI vs AI mode
    ai_move = players[idx].get_move(_GameView(board))
    board.make_move(ai_move[0], ai_move[1], players[idx].letter)
    _save_board(board)
    session['current_player_index'] = 1 - idx
    return jsonify(_state())

@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify(_state())

if __name__ == "__main__":
    app.run(debug=True, port=5000)