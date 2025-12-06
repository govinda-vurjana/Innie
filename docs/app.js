const POST_W = 1080;
const POST_H = 1350;

let sourceImage = null;
let sourceName = '';
let tiles = [];

// DOM Elements
const imageInput = document.getElementById('imageInput');
const fileName = document.getElementById('fileName');
const dropZone = document.getElementById('dropZone');
const gridCount = document.getElementById('gridCount');
const mode = document.getElementById('mode');
const marginTB = document.getElementById('marginTB');
const marginSide = document.getElementById('marginSide');
const frameEnabled = document.getElementById('frameEnabled');
const frameStyle = document.getElementById('frameStyle');
const frameThickness = document.getElementById('frameThickness');
const renderBtn = document.getElementById('renderBtn');
const saveBtn = document.getElementById('saveBtn');
const clearBtn = document.getElementById('clearBtn');
const previewGrid = document.getElementById('previewGrid');
const statusEl = document.getElementById('status');

// Event Listeners
imageInput.addEventListener('change', handleImageSelect);
gridCount.addEventListener('change', updateGridDisplay);
renderBtn.addEventListener('click', renderPreview);
saveBtn.addEventListener('click', downloadZip);
clearBtn.addEventListener('click', clearAll);

// Initialize grid display
updateGridDisplay();

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    sourceName = file.name.replace(/\.[^/.]+$/, '');
    fileName.textContent = file.name;
    
    // Update drop zone text
    const uploadText = dropZone.querySelector('.upload-text');
    if (uploadText) {
        uploadText.innerHTML = '<strong>Change image</strong> or drag another';
    }

    const reader = new FileReader();
    reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
            sourceImage = img;
            setStatus(`Loaded: ${img.width}×${img.height}`);
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

function updateGridDisplay() {
    const count = parseInt(gridCount.value);
    const rows = count / 3;
    
    previewGrid.innerHTML = '';
    for (let i = 1; i <= count; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.id = `cell-${i}`;
        cell.textContent = `Grid ${i}`;
        previewGrid.appendChild(cell);
    }
    
    tiles = [];
}

function renderPreview() {
    if (!sourceImage) {
        alert('Please select an image first');
        return;
    }

    const count = parseInt(gridCount.value);
    const rows = count / 3;
    const cols = 3;
    const Mt = parseInt(marginTB.value);
    const Ms = parseInt(marginSide.value);
    const modeVal = mode.value;
    const frameOn = frameEnabled.checked;
    const frameStyleVal = frameStyle.value;
    const frameThick = parseInt(frameThickness.value);

    // Validate margins
    if (Ms * 2 >= POST_W) {
        alert('Side margins too large');
        return;
    }
    if (rows === 1 && Mt * 2 >= POST_H) {
        alert('Top/bottom margins too large');
        return;
    }

    // Calculate content dimensions
    const contentWidths = [];
    for (let c = 0; c < cols; c++) {
        const leftM = c === 0 ? Ms : 0;
        const rightM = c === cols - 1 ? Ms : 0;
        contentWidths.push(POST_W - leftM - rightM);
    }

    const contentHeights = [];
    for (let r = 0; r < rows; r++) {
        let topM, bottomM;
        if (rows === 1) {
            topM = Mt;
            bottomM = Mt;
        } else {
            topM = r === 0 ? Mt : 0;
            bottomM = r === rows - 1 ? Mt : 0;
        }
        contentHeights.push(POST_H - topM - bottomM);
    }

    const W_visible = contentWidths.reduce((a, b) => a + b, 0);
    const H_visible = contentHeights.reduce((a, b) => a + b, 0);

    // Resize source image
    const resizedCanvas = document.createElement('canvas');
    resizedCanvas.width = W_visible;
    resizedCanvas.height = H_visible;
    const resizedCtx = resizedCanvas.getContext('2d');

    if (modeVal === 'cover') {
        resizeCover(resizedCtx, sourceImage, W_visible, H_visible);
    } else {
        resizeFit(resizedCtx, sourceImage, W_visible, H_visible);
    }

    // Cumulative positions
    const cumW = [0];
    for (let i = 0; i < contentWidths.length - 1; i++) {
        cumW.push(cumW[i] + contentWidths[i]);
    }

    const cumH = [0];
    for (let i = 0; i < contentHeights.length - 1; i++) {
        cumH.push(cumH[i] + contentHeights[i]);
    }

    // Generate tiles
    tiles = [];
    let index = 1;

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const x0 = cumW[c];
            const y0 = cumH[r];
            const cw = contentWidths[c];
            const ch = contentHeights[r];

            // Margins for this tile
            let topM, bottomM;
            if (rows === 1) {
                topM = Mt;
                bottomM = Mt;
            } else {
                topM = r === 0 ? Mt : 0;
                bottomM = r === rows - 1 ? Mt : 0;
            }
            const leftM = c === 0 ? Ms : 0;

            // Create tile canvas
            const tileCanvas = document.createElement('canvas');
            tileCanvas.width = POST_W;
            tileCanvas.height = POST_H;
            const ctx = tileCanvas.getContext('2d');

            // Fill black background
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, POST_W, POST_H);

            // Draw content
            ctx.drawImage(resizedCanvas, x0, y0, cw, ch, leftM, topM, cw, ch);

            // Draw frame
            if (frameOn) {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;

                const fl = leftM;
                const ft = topM;
                const fr = leftM + cw - 1;
                const fb = topM + ch - 1;

                if (frameStyleVal === 'outer') {
                    // Frame only on outer edges
                    for (let t = 0; t < frameThick; t++) {
                        if (r === 0) drawLine(ctx, fl, ft + t, fr, ft + t);
                        if (r === rows - 1) drawLine(ctx, fl, fb - t, fr, fb - t);
                        if (c === 0) drawLine(ctx, fl + t, ft, fl + t, fb);
                        if (c === cols - 1) drawLine(ctx, fr - t, ft, fr - t, fb);
                    }
                } else {
                    // Individual frame on each tile's content
                    for (let t = 0; t < frameThick; t++) {
                        drawLine(ctx, leftM, topM + t, leftM + cw - 1, topM + t);
                        drawLine(ctx, leftM, topM + ch - 1 - t, leftM + cw - 1, topM + ch - 1 - t);
                        drawLine(ctx, leftM + t, topM, leftM + t, topM + ch - 1);
                        drawLine(ctx, leftM + cw - 1 - t, topM, leftM + cw - 1 - t, topM + ch - 1);
                    }
                }
            }

            tiles.push(tileCanvas);

            // Update preview
            const cell = document.getElementById(`cell-${index}`);
            cell.innerHTML = '';
            const img = document.createElement('img');
            img.src = tileCanvas.toDataURL('image/png');
            cell.appendChild(img);

            index++;
        }
    }

    setStatus('Preview rendered successfully');
}

function drawLine(ctx, x1, y1, x2, y2) {
    ctx.beginPath();
    ctx.moveTo(x1 + 0.5, y1 + 0.5);
    ctx.lineTo(x2 + 0.5, y2 + 0.5);
    ctx.stroke();
}

function resizeCover(ctx, img, targetW, targetH) {
    const scale = Math.max(targetW / img.width, targetH / img.height);
    const newW = Math.ceil(img.width * scale);
    const newH = Math.ceil(img.height * scale);
    const left = (newW - targetW) / 2;
    const top = (newH - targetH) / 2;
    
    ctx.drawImage(img, -left, -top, newW, newH);
}

function resizeFit(ctx, img, targetW, targetH) {
    const scale = Math.min(targetW / img.width, targetH / img.height);
    const newW = Math.round(img.width * scale);
    const newH = Math.round(img.height * scale);
    const left = (targetW - newW) / 2;
    const top = (targetH - newH) / 2;
    
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, targetW, targetH);
    ctx.drawImage(img, left, top, newW, newH);
}

async function downloadZip() {
    if (tiles.length === 0) {
        alert('Please render preview first');
        return;
    }

    setStatus('Creating ZIP file...');

    const zip = new JSZip();
    const folder = zip.folder(`${sourceName}_grid_${gridCount.value}`);

    // Add tiles
    for (let i = 0; i < tiles.length; i++) {
        const dataUrl = tiles[i].toDataURL('image/png');
        const base64 = dataUrl.split(',')[1];
        folder.file(`grid_${String(i + 1).padStart(2, '0')}.png`, base64, {base64: true});
    }

    // Create and add preview
    const previewCanvas = createPreviewImage();
    const previewData = previewCanvas.toDataURL('image/png').split(',')[1];
    folder.file('preview_grid.png', previewData, {base64: true});

    // Generate and download
    const content = await zip.generateAsync({type: 'blob'});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(content);
    link.download = `${sourceName}_grid_${gridCount.value}.zip`;
    link.click();

    setStatus('ZIP downloaded successfully');
}

function createPreviewImage() {
    const count = parseInt(gridCount.value);
    const rows = count / 3;
    const cols = 3;

    const canvas = document.createElement('canvas');
    canvas.width = cols * POST_W;
    canvas.height = rows * POST_H;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < tiles.length; i++) {
        const row = Math.floor(i / cols);
        const col = i % cols;
        ctx.drawImage(tiles[i], col * POST_W, row * POST_H);
    }

    return canvas;
}

function clearAll() {
    sourceImage = null;
    sourceName = '';
    tiles = [];
    fileName.textContent = '';
    imageInput.value = '';
    
    // Reset drop zone text
    const uploadText = dropZone.querySelector('.upload-text');
    if (uploadText) {
        uploadText.innerHTML = '<strong>Click to upload</strong> or drag & drop';
    }
    
    updateGridDisplay();
    setStatus('Cleared all');
}

function setStatus(msg) {
    statusEl.textContent = msg;
    if (msg.includes('success') || msg.includes('Loaded')) {
        statusEl.classList.add('success');
    } else {
        statusEl.classList.remove('success');
    }
}
