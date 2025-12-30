import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Math Tetris with Sound", layout="centered")

st.title("🔢 Math Tetris (Sound Edition) 🔊")
st.info("⚠️ **වැදගත්:** ශබ්ද ඇසීමට සහ Control කිරීමට කලින් Game Area එක මත එක පාරක් Click කරන්න.")

math_tetris_html = """
<div id="game-container" style="text-align: center; font-family: 'Segoe UI', Arial, sans-serif; color: white; background: #222; padding: 20px; border-radius: 20px;">
    <canvas id="tetris" width="240" height="400" style="border: 4px solid #555; background-color: #000; border-radius: 10px;"></canvas>
    <div style="margin-top: 15px; font-size: 28px;">Score: <span id="score" style="color: #0DFF72;">0</span></div>
</div>

<script>
// --- ශබ්ද නිර්මාණය කිරීම (Web Audio API) ---
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playTone(freq, type, duration) {
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + duration);
}

const moveSound = () => playTone(150, 'sine', 0.1);
const rotateSound = () => playTone(300, 'square', 0.05);
const clearSound = () => {
    playTone(523.25, 'triangle', 0.2); // C5
    setTimeout(() => playTone(659.25, 'triangle', 0.2), 100); // E5
    setTimeout(() => playTone(783.99, 'triangle', 0.4), 200); // G5
};

// --- Tetris Logic ---
const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');
const scoreElement = document.getElementById('score');

context.scale(20, 20);

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
        updateScore();
        clearSound(); // ශබ්දය ප්ලේ වේ
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
    const num = Math.floor(Math.random() * 9) + 1;
    if (type === 'I') return [[0, num, 0, 0], [0, num, 0, 0], [0, num, 0, 0], [0, num, 0, 0]];
    if (type === 'L') return [[0, num, 0], [0, num, 0], [0, num, num]];
    if (type === 'J') return [[0, num, 0], [0, num, 0], [num, num, 0]];
    if (type === 'O') return [[num, num], [num, num]];
    if (type === 'Z') return [[num, num, 0], [0, num, num], [0, 0, 0]];
    if (type === 'S') return [[0, num, num], [num, num, 0], [0, 0, 0]];
    if (type === 'T') return [[0, num, 0], [num, num, num], [0, 0, 0]];
}

function drawMatrix(matrix, offset) {
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                context.fillStyle = colors[value % 8 || 1];
                context.fillRect(x + offset.x, y + offset.y, 1, 1);
                context.fillStyle = 'white';
                context.font = '0.7px Arial';
                context.fillText(value, x + offset.x + 0.25, y + offset.y + 0.75);
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
    else moveSound();
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
    rotateSound();
}

function playerReset() {
    const pieces = 'ILJOTSZ';
    player.matrix = createPiece(pieces[pieces.length * Math.random() | 0]);
    player.pos.y = 0;
    player.pos.x = (arena[0].length / 2 | 0) - (player.matrix[0].length / 2 | 0);
    if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
        player.score = 0;
        updateScore();
    }
}

let dropCounter = 0;
let dropInterval = 1000;
let lastTime = 0;

function update(time = 0) {
    const deltaTime = time - lastTime;
    lastTime = time;
    dropCounter += deltaTime;
    if (dropCounter > dropInterval) playerDrop();
    draw();
    requestAnimationFrame(update);
}

function updateScore() {
    scoreElement.innerText = player.score;
}

const colors = [null, '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF', '#FF8E0D', '#FFE138', '#3877FF'];
const arena = Array.from({length: 20}, () => new Array(12).fill(0));
const player = { pos: {x: 0, y: 0}, matrix: null, score: 0 };

window.addEventListener('keydown', event => {
    if (audioCtx.state === 'suspended') audioCtx.resume(); // Chrome audio policy fix
    if([37, 38, 39, 40].includes(event.keyCode)) event.preventDefault();
    if (event.keyCode === 37) playerMove(-1);
    else if (event.keyCode === 39) playerMove(1);
    else if (event.keyCode === 40) playerDrop();
    else if (event.keyCode === 38) playerRotate(1);
});

playerReset();
updateScore();
update();
</script>
"""

components.html(math_tetris_html, height=600)
