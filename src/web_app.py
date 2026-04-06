"""
Minimal web UI for the existing Tic Tac Toe game (same modes as src/main.py).
Run: python src/web_app.py  (from repo root)  or  cd src && python web_app.py
"""
import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from flask import Flask, Response, jsonify, request, session

from board import Board
from player import AIPlayer, HumanPlayer

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-tic-tac-toe-key")


class _GameView:
    def __init__(self, board):
        self.board = board


def _players_and_start(mode, human_letter=None):
    """Match main.py Game.setup() player order and starting index."""
    if mode == 1:
        hl = human_letter.upper()
        ai_letter = "O" if hl == "X" else "X"
        players = [HumanPlayer(hl), AIPlayer(ai_letter, "hard")]
        start = 1 if hl == "O" else 0
        return players, start
    if mode == 2:
        return [AIPlayer("X", "hard"), AIPlayer("O", "hard")], 0
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
    done = winner in ("X", "O", "Draw")
    mode = session.get("mode")
    phase = session.get("phase", "setup")
    players = []
    cur_idx = 0
    if mode and phase == "playing":
        hl = session.get("human_letter")
        players, _ = _players_and_start(mode, hl)
        cur_idx = session.get("current_player_index", 0)

    cur_letter = None
    human_turn = False
    need_ai_step = False
    if mode and phase == "playing" and not done:
        cur = players[cur_idx]
        cur_letter = cur.letter
        human_turn = isinstance(cur, HumanPlayer)
        need_ai_step = isinstance(cur, AIPlayer) and mode == 2

    return {
        "phase": phase,
        "mode": mode,
        "human_letter": session.get("human_letter"),
        "board": board.grid,
        "winner": winner,
        "done": done,
        "current_letter": cur_letter,
        "human_turn": human_turn,
        "need_ai_step": need_ai_step,
    }


def _run_ai_move(board, players, cur_idx):
    cur = players[cur_idx]
    row, col = cur.get_move(_GameView(board))
    board.make_move(row, col, cur.letter)


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tic Tac Toe</title>
<style>
  html { box-sizing: border-box; }
  *, *::before, *::after { box-sizing: inherit; }
  body {
    font-family: system-ui, Segoe UI, sans-serif;
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    color: #222;
    background: #fafafa;
    text-align: center;
  }
  h1 { font-size: 1.25rem; font-weight: 600; margin: 0 0 1rem; width: 100%; max-width: 24rem; }
  #setup, #play { width: 100%; max-width: 24rem; }
  fieldset { border: 1px solid #ccc; margin: 0 auto 1rem; padding: 0.75rem; background: #fff; text-align: center; }
  legend { padding: 0 0.35rem; margin: 0 auto; }
  label { display: block; margin: 0.35rem 0; cursor: pointer; }
  .row { margin: 0.5rem 0; display: flex; justify-content: center; flex-wrap: wrap; gap: 0.5rem; }
  button, .btn { font-size: 0.95rem; padding: 0.35rem 0.75rem; background: #e8e8e8; border: 1px solid #999; cursor: pointer; color: #222; }
  button:disabled { opacity: 0.5; cursor: default; }
  #status { min-height: 1.4em; margin: 0.75rem auto; max-width: 24rem; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 0.75rem auto; width: 100%; max-width: 12rem; }
  .cell { min-height: 3.25rem; font-size: 1.35rem; background: #fff; border: 1px solid #bbb; cursor: pointer; color: #111; }
  .cell:disabled { cursor: default; background: #eee; }
  .hidden { display: none; }
</style>
</head>
<body>
<h1>Tic Tac Toe</h1>

<div id="setup">
  <fieldset>
    <legend>Mode</legend>
    <label><input type="radio" name="mode" value="1" checked> Human vs AI</label>
    <label><input type="radio" name="mode" value="2"> AI vs AI (demo)</label>
    <label><input type="radio" name="mode" value="3"> Human vs Human</label>
  </fieldset>
  <fieldset id="xoPick">
    <legend>Play as (Human vs AI)</legend>
    <label><input type="radio" name="hl" value="X" checked> X</label>
    <label><input type="radio" name="hl" value="O"> O</label>
  </fieldset>
  <button type="button" id="start">Start game</button>
</div>

<div id="play" class="hidden">
  <div id="status"></div>
  <div class="grid" id="board"></div>
  <div class="row">
    <button type="button" id="aiStep" class="hidden">AI move</button>
  </div>
  <div class="row">
    <button type="button" id="newGame">New game</button>
  </div>
</div>

<script>
async function api(path, opts) {
  const r = await fetch(path, Object.assign({ credentials: 'same-origin', headers: { 'Content-Type': 'application/json' } }, opts || {}));
  const t = await r.text();
  let j = null;
  try { j = JSON.parse(t); } catch (e) {}
  if (!r.ok) throw new Error(j && j.error ? j.error : t);
  return j;
}

function modeValue() {
  const m = document.querySelector('input[name="mode"]:checked');
  return m ? parseInt(m.value, 10) : 1;
}

function hlValue() {
  const h = document.querySelector('input[name="hl"]:checked');
  return h ? h.value : 'X';
}

function render(s) {
  const setupEl = document.getElementById('setup');
  const playEl = document.getElementById('play');
  const status = document.getElementById('status');
  const boardEl = document.getElementById('board');
  const aiStep = document.getElementById('aiStep');
  const xoPick = document.getElementById('xoPick');

  document.querySelectorAll('input[name="mode"]').forEach(function (el) {
    el.onchange = function () { xoPick.classList.toggle('hidden', modeValue() !== 1); };
  });
  xoPick.classList.toggle('hidden', modeValue() !== 1);

  if (s.phase === 'setup') {
    setupEl.classList.remove('hidden');
    playEl.classList.add('hidden');
    return;
  }
  setupEl.classList.add('hidden');
  playEl.classList.remove('hidden');

  boardEl.innerHTML = '';
  const done = s.done;
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const ch = s.board[r][c];
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'cell';
      btn.textContent = ch === ' ' ? '' : ch;
      const canClick = s.human_turn && !done && ch === ' ';
      btn.disabled = !canClick;
      if (canClick) btn.addEventListener('click', function () { move(r, c); });
      boardEl.appendChild(btn);
    }
  }

  aiStep.classList.toggle('hidden', !s.need_ai_step || done);
  aiStep.disabled = done;

  let msg = '';
  if (s.winner === 'Draw') msg = "It's a draw.";
  else if (s.winner === 'X' || s.winner === 'O') msg = s.winner + ' wins.';
  else if (s.need_ai_step) msg = 'AI vs AI — click “AI move” for the next play.';
  else if (s.current_letter) msg = s.current_letter + "'s turn.";
  status.textContent = msg;
}

async function move(row, col) {
  const s = await api('/api/move', { method: 'POST', body: JSON.stringify({ row: row, col: col }) });
  render(s);
}

document.getElementById('aiStep').addEventListener('click', async function () {
  const s = await api('/api/ai_step', { method: 'POST', body: '{}' });
  render(s);
});

document.getElementById('start').addEventListener('click', async function () {
  const mode = modeValue();
  const body = { mode: mode };
  if (mode === 1) body.humanLetter = hlValue();
  const s = await api('/api/configure', { method: 'POST', body: JSON.stringify(body) });
  render(s);
});

document.getElementById('newGame').addEventListener('click', async function () {
  const s = await api('/api/reset', { method: 'POST' });
  render(s);
});

(async function init() {
  const s = await api('/api/state', { method: 'GET' });
  render(s);
})();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html; charset=utf-8")


@app.route("/api/state", methods=["GET"])
def get_state():
    if "phase" not in session:
        session["phase"] = "setup"
    return jsonify(_state())


@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    session["phase"] = "setup"
    return jsonify(_state())


@app.route("/api/configure", methods=["POST"])
def configure():
    data = request.get_json(silent=True) or {}
    try:
        mode = int(data["mode"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "mode must be 1, 2, or 3"}), 400
    if mode not in (1, 2, 3):
        return jsonify({"error": "mode must be 1, 2, or 3"}), 400

    human_letter = None
    if mode == 1:
        hl = (data.get("humanLetter") or data.get("human_letter") or "X").upper()
        if hl not in ("X", "O"):
            return jsonify({"error": "humanLetter must be X or O"}), 400
        human_letter = hl

    session["mode"] = mode
    session["human_letter"] = human_letter
    session["phase"] = "playing"
    b = Board()
    session["grid"] = [row[:] for row in b.grid]
    players, start = _players_and_start(mode, human_letter or "X")
    session["current_player_index"] = start

    board = _load_board()
    winner = board.check_winner()

    # Human vs AI with human as O: AI (X) opens — same as CLI after setup()
    if mode == 1 and isinstance(players[start], AIPlayer):
        _run_ai_move(board, players, start)
        _save_board(board)
        winner = board.check_winner()
        if winner not in ("X", "O", "Draw"):
            session["current_player_index"] = 1 - start

    return jsonify(_state())


@app.route("/api/move", methods=["POST"])
def move():
    if session.get("phase") != "playing":
        return jsonify({"error": "start a game first"}), 400

    data = request.get_json(silent=True) or {}
    try:
        row = int(data["row"])
        col = int(data["col"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "expected row and col"}), 400

    mode = session["mode"]
    hl = session.get("human_letter")
    players, _ = _players_and_start(mode, hl or "X")
    idx = session["current_player_index"]
    board = _load_board()

    winner = board.check_winner()
    if winner in ("X", "O", "Draw"):
        return jsonify(_state())

    cur = players[idx]
    if not isinstance(cur, HumanPlayer):
        return jsonify({"error": "not human's turn"}), 400

    if not board.make_move(row, col, cur.letter):
        return jsonify({"error": "invalid move"}), 400

    _save_board(board)
    winner = board.check_winner()
    if winner in ("X", "O", "Draw"):
        return jsonify(_state())

    session["current_player_index"] = 1 - idx
    idx2 = session["current_player_index"]
    next_p = players[idx2]

    if isinstance(next_p, AIPlayer):
        _run_ai_move(board, players, idx2)
        _save_board(board)
        winner = board.check_winner()
        if winner not in ("X", "O", "Draw"):
            session["current_player_index"] = 1 - idx2

    return jsonify(_state())


@app.route("/api/ai_step", methods=["POST"])
def ai_step():
    if session.get("phase") != "playing":
        return jsonify({"error": "start a game first"}), 400
    if session.get("mode") != 2:
        return jsonify({"error": "AI step only for AI vs AI mode"}), 400

    players, _ = _players_and_start(2, None)
    idx = session["current_player_index"]
    board = _load_board()

    winner = board.check_winner()
    if winner in ("X", "O", "Draw"):
        return jsonify(_state())

    cur = players[idx]
    if not isinstance(cur, AIPlayer):
        return jsonify({"error": "not an AI turn"}), 400

    _run_ai_move(board, players, idx)
    _save_board(board)
    winner = board.check_winner()
    if winner not in ("X", "O", "Draw"):
        session["current_player_index"] = 1 - idx

    return jsonify(_state())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
