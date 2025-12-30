import streamlit as st
import streamlit.components.v1 as components

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Big Math Tetris", layout="centered")

st.title("🔢 Math Tetris (Big & Sound) 🔊")
st.info("💡 **උපදෙස්:** ක්‍රීඩාව ඇරඹීමට පහත කළු තිරය මත එක පාරක් Click කරන්න. ඉන්පසු Arrow Keys පාවිච්චි කරන්න.")

# HTML සහ JavaScript කොටස
math_tetris_html = """
<div id="game-container" style="text-align: center; font-family: sans-serif; color: white; background: #1e1e1e; padding: 20px; border-radius: 20px;">
    <canvas id="tetris" width="400" height="600" style="border: 5px solid #444; background-color: #000; border-radius: 10px;"></canvas>
    <div style="margin-top: 15px; font-size: 32px; font-weight: bold;">Score: <span id="score" style="color: #0DFF72;">0</span></div>
</div>

<script>
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playTone(freq, type, duration) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
}

const moveSnd = () => playTone(150, 'sine', 0.1);
const rotateSnd = () => playTone(300, 'square', 0.05);
const clearSnd = () => {
    playTone(523, 'triangle', 0.2);
    setTimeout(() => playTone(659, 'triangle', 0.2), 100);
    setTimeout(() => playTone(783, 'triangle', 0.4), 200);
};

const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');
const scoreElement = document.getElementById('score');

context.scale(33.3, 33.3);

function arenaSweep() {
    let rowScore = 0;
    outer: for (let y = arena.length - 1; y > 0; --y) {
        for (let x = 0; x < arena[y].length; ++x) {
            if (arena[y][x] === 0) continue outer;
        }
        arena[y].forEach(val => rowScore += val);
        arena.splice(y, 1);
        arena.unshift(new Array(12).fill(0));
        ++y;
    }
    if (rowScore > 0) {
        player.score += rowScore;
        scoreElement.innerText = player.score;
        clearSnd();
    }
}

function collide(arena, player) {
    const [m, o] = [player.matrix, player.pos];
    for (let y = 0; y < m.length; ++y) {
        for (let x = 0; x < m[y].length; ++x) {
            if (m[y][x] !== 0 && (arena[y + o.y] && arena[y + o.y][x + o.x]) !== 0) return true;
        }
    }
    return false;
}

function createPiece(type) {
    const n = Math.floor(Math.random() * 9) + 1;
    if (type === 'I') return [[0,n,0,0],[0,n,0,0],[0,n,0,0],[0,n,0,0]];
    if (type === 'L') return [[0,n,0],[0,n,0],[0,n,n]];
    if (type === 'J') return [[0,n,0],[0,n,0],[n,n,0]];
    if (type === 'O') return [[n,n],[n,n]];
    if (type === 'Z') return [[n,n,0],[0,n,n],[0,0,0]];
    if (type === 'S') return [[0,n,n],[n,n,0],[0,0,0]];
    if (type === 'T') return [[0,n,0],[n,n,n],[0,0,0]];
}

function drawMatrix(matrix, offset) {
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                context.fillStyle = colors[value % 8 || 1];
                context.fillRect(x + offset.x, y + offset.y, 1, 1);
                context.fillStyle = 'white';
                context.font = '0.6px Arial';
                context.fillText(value, x + offset.x + 0.3, y + offset.y + 0.75);
            }
        });
    });
}

function draw() {
    context.fillStyle = '#000';
    context.fillRect(0, 0, canvas.width, canvas.height);
    drawMatrix(arena, {x: 0, y: 0});
    drawMatrix(player.matrix, player.pos);
}

function merge(arena, player) {
    player.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) arena[y + player.pos.y][x + player.pos.x] = value;
        });
    });
}

function playerDrop() {
    player.pos.y++;
    if (collide(arena, player)) {
        player.pos.y--;
        merge(arena, player);
        playerReset();
        arenaSweep();
    }
    dropCounter = 0;
}

function playerMove(dir) {
    player.pos.x += dir;
    if (collide(arena, player)) player.pos.x -= dir;
    else moveSnd();
}

function rotate(matrix, dir) {
    for (let y = 0; y < matrix.length; ++y) {
        for (let x = 0; x < y; ++x) [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
    }
    if (dir > 0) matrix.forEach(row => row.reverse()); else matrix.reverse();
}

function playerRotate(dir) {
    const pos = player.pos.x;
    let offset = 1;
    rotate(player.matrix, dir);
    while (collide(arena, player)) {
        player.pos.x += offset;
        offset = -(offset + (offset > 0 ? 1 : -1));
        if (offset > player.matrix[0].length) {
            rotate(player.matrix, -dir);
            player.pos.x = pos;
            return;
        }
    }
    rotateSnd();
}

function playerReset() {
    const p = 'ILJOTSZ';
    player.matrix = createPiece(p[p.length * Math.random() | 0]);
    player.pos.y = 0;
    player.pos.x = (arena[0].length / 2 | 0) - (player.matrix[0].length / 2 | 0);
    if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
        player.score = 0;
        scoreElement.innerText = 0;
    }
}

let dropCounter = 0;
let lastTime = 0;
function update(time = 0) {
    const dt = time - lastTime;
    lastTime = time;
    dropCounter += dt;
    if (dropCounter > 1000) playerDrop();
    draw();
    requestAnimationFrame(update);
}

const colors = [null, '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF', '#FF8E0D', '#FFE138', '#3877FF'];
const arena = Array.from({length: 18}, () => new Array(12).fill(0));
const player = { pos: {x: 0, y: 0}, matrix: null, score: 0 };

window.addEventListener('keydown', e => {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    if([37, 38, 39, 40].includes(e.keyCode)) e.preventDefault();
    if (e.keyCode === 37) playerMove(-1);
    else if (e.keyCode === 39) playerMove(1);
    else if (e.keyCode === 40) playerDrop();
    else if (e.keyCode === 38) playerRotate(1);
});

playerReset();
update();
</script>
"""

# මෙතන height එක 800 දක්වා වැඩි කළා ලොකු පෙනුම සඳහා
components.html(math_tetris_html, height=800)
