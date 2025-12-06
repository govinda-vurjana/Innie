const POST_W = 1080;
const POST_H = 1350;

let sourceImage = null;
let sourceName = '';
let tiles = [];

// DOM Elements
const imageInput = document.getElementById('imageInput');
const fileName = document.getElementById('fileName');
const dropZone = document.getElementById('dropZone');
const imageThumb = document.getElementById('imageThumb');
const thumbImg = document.getElementById('thumbImg');
const removeImage = document.getElementById('removeImage');
const gridCount = document.getElementById('gridCount');
const mode = document.getElementById('mode');
const marginTB = document.getElementById('marginTB');
const marginSide = document.getElementById('marginSide');
const frameEnabled = document.getElementById('frameEnabled');
const frameStyle = document.getElementById('frameStyle');
const frameThickness = document.getElementById('frameThickness');
const renderBtn = document.getElementById('renderBtn');
const saveBtn = document.getElementById('saveBtn');
const previewGrid = document.getElementById('previewGrid');
const toast = document.getElementById('toast');

// Event Listeners
imageInput.addEventListener('change', handleImageSelect);
gridCount.addEventListener('change', updateGridDisplay);
renderBtn.addEventListener('click', renderPreview);
saveBtn.addEventListener('click', downloadImages);
removeImage.addEventListener('click', clearImage);

// Drop zone events
dropZone.addEventListener('click', () => imageInput.click());
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        imageInput.files = e.dataTransfer.files;
        imageInput.dispatchEvent(new Event('change'));
    }
});

// Initialize
updateGridDisplay();

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    sourceName = file.name.replace(/\.[^/.]+$/, '');
    fileName.textContent = file.name;

    const reader = new FileReader();
    reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
            sourceImage = img;
            thumbImg.src = event.target.result;
            dropZone.style.display = 'none';
            imageThumb.classList.add('active');
            showToast(`Loaded: ${img.width}×${img.height}`, true);
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

function clearImage() {
    sourceImage = null;
    sourceName = '';
    imageInput.value = '';
    fileName.textContent = '';
    thumbImg.src = '';
    dropZone.style.display = 'block';
    imageThumb.classList.remove('active');
    tiles = [];
    updateGridDisplay();
}

function updateGridDisplay() {
    const count = parseInt(gridCount.value);
    previewGrid.innerHTML = '';
    
    for (let i = 1; i <= count; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.id = `cell-${i}`;
        cell.setAttribute('data-index', i);
        cell.textContent = i;
        previewGrid.appendChild(cell);
    }
    tiles = [];
}

function renderPreview() {
    if (!sourceImage) {
        showToast('Please select an image first');
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

    if (Ms * 2 >= POST_W || (rows === 1 && Mt * 2 >= POST_H)) {
        showToast('Margins too large');
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
        const topM = rows === 1 ? Mt : (r === 0 ? Mt : 0);
        const bottomM = rows === 1 ? Mt : (r === rows - 1 ? Mt : 0);
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
    for (let i = 0; i < contentWidths.length - 1; i++) cumW.push(cumW[i] + contentWidths[i]);
    const cumH = [0];
    for (let i = 0; i < contentHeights.length - 1; i++) cumH.push(cumH[i] + contentHeights[i]);

    // Generate tiles
    tiles = [];
    let index = 1;

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const x0 = cumW[c], y0 = cumH[r];
            const cw = contentWidths[c], ch = contentHeights[r];
            const topM = rows === 1 ? Mt : (r === 0 ? Mt : 0);
            const leftM = c === 0 ? Ms : 0;

            const tileCanvas = document.createElement('canvas');
            tileCanvas.width = POST_W;
            tileCanvas.height = POST_H;
            const ctx = tileCanvas.getContext('2d');

            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, POST_W, POST_H);
            ctx.drawImage(resizedCanvas, x0, y0, cw, ch, leftM, topM, cw, ch);

            // Draw frame
            if (frameOn) {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                const fl = leftM, ft = topM, fr = leftM + cw - 1, fb = topM + ch - 1;

                if (frameStyleVal === 'outer') {
                    for (let t = 0; t < frameThick; t++) {
                        if (r === 0) drawLine(ctx, fl, ft + t, fr, ft + t);
                        if (r === rows - 1) drawLine(ctx, fl, fb - t, fr, fb - t);
                        if (c === 0) drawLine(ctx, fl + t, ft, fl + t, fb);
                        if (c === cols - 1) drawLine(ctx, fr - t, ft, fr - t, fb);
                    }
                } else {
                    if (modeVal === 'fit') {
                        const bounds = getImageBounds(ctx, leftM, topM, cw, ch);
                        if (bounds) {
                            const { ix0, iy0, ix1, iy1 } = bounds;
                            for (let t = 0; t < frameThick; t++) {
                                if (r === 0) drawLine(ctx, ix0, iy0 + t, ix1, iy0 + t);
                                if (r === rows - 1) drawLine(ctx, ix0, iy1 - t, ix1, iy1 - t);
                                if (c === 0) drawLine(ctx, ix0 + t, iy0, ix0 + t, iy1);
                                if (c === cols - 1) drawLine(ctx, ix1 - t, iy0, ix1 - t, iy1);
                            }
                        }
                    } else {
                        for (let t = 0; t < frameThick; t++) {
                            drawLine(ctx, fl, ft + t, fr, ft + t);
                            drawLine(ctx, fl, fb - t, fr, fb - t);
                            drawLine(ctx, fl + t, ft, fl + t, fb);
                            drawLine(ctx, fr - t, ft, fr - t, fb);
                        }
                    }
                }
            }

            tiles.push(tileCanvas);

            const cell = document.getElementById(`cell-${index}`);
            cell.innerHTML = '';
            const img = document.createElement('img');
            img.src = tileCanvas.toDataURL('image/png');
            cell.appendChild(img);
            index++;
        }
    }

    showToast('Rendered successfully!', true);
}

function drawLine(ctx, x1, y1, x2, y2) {
    ctx.beginPath();
    ctx.moveTo(x1 + 0.5, y1 + 0.5);
    ctx.lineTo(x2 + 0.5, y2 + 0.5);
    ctx.stroke();
}

function getImageBounds(ctx, startX, startY, width, height) {
    const imageData = ctx.getImageData(startX, startY, width, height);
    const data = imageData.data;
    let minX = width, minY = height, maxX = -1, maxY = -1;

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const idx = (y * width + x) * 4;
            if (data[idx] > 5 || data[idx + 1] > 5 || data[idx + 2] > 5) {
                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            }
        }
    }

    if (maxX < 0) return null;
    return { ix0: startX + minX, iy0: startY + minY, ix1: startX + maxX, iy1: startY + maxY };
}

function resizeCover(ctx, img, targetW, targetH) {
    const scale = Math.max(targetW / img.width, targetH / img.height);
    const newW = Math.ceil(img.width * scale);
    const newH = Math.ceil(img.height * scale);
    ctx.drawImage(img, -(newW - targetW) / 2, -(newH - targetH) / 2, newW, newH);
}

function resizeFit(ctx, img, targetW, targetH) {
    const scale = Math.min(targetW / img.width, targetH / img.height);
    const newW = Math.round(img.width * scale);
    const newH = Math.round(img.height * scale);
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, targetW, targetH);
    ctx.drawImage(img, (targetW - newW) / 2, (targetH - newH) / 2, newW, newH);
}

async function downloadImages() {
    if (tiles.length === 0) {
        showToast('Please render preview first');
        return;
    }

    const useZip = confirm('Download as ZIP?\n\nOK = ZIP file\nCancel = Individual PNGs');
    
    if (useZip) {
        showToast('Creating ZIP...');
        const zip = new JSZip();
        const folder = zip.folder(`${sourceName}_grid_${gridCount.value}`);
        
        for (let i = 0; i < tiles.length; i++) {
            const base64 = tiles[i].toDataURL('image/png').split(',')[1];
            folder.file(`grid_${String(i + 1).padStart(2, '0')}.png`, base64, { base64: true });
        }
        
        const previewCanvas = createPreviewImage();
        folder.file('preview_grid.png', previewCanvas.toDataURL('image/png').split(',')[1], { base64: true });
        
        const content = await zip.generateAsync({ type: 'blob' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(content);
        link.download = `${sourceName}_grid_${gridCount.value}.zip`;
        link.click();
        showToast('ZIP downloaded!', true);
    } else {
        showToast('Downloading files...');
        const prefix = `${sourceName}_g${gridCount.value}`;
        
        for (let i = 0; i < tiles.length; i++) {
            await downloadCanvas(tiles[i], `${prefix}_${String(i + 1).padStart(2, '0')}.png`);
            await new Promise(r => setTimeout(r, 150));
        }
        
        await downloadCanvas(createPreviewImage(), `${prefix}_preview.png`);
        showToast(`Downloaded ${tiles.length + 1} files!`, true);
    }
}

function downloadCanvas(canvas, filename) {
    return new Promise(resolve => {
        canvas.toBlob(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
            resolve();
        }, 'image/png');
    });
}

function createPreviewImage() {
    const count = parseInt(gridCount.value);
    const rows = count / 3, cols = 3;
    const canvas = document.createElement('canvas');
    canvas.width = cols * POST_W;
    canvas.height = rows * POST_H;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    for (let i = 0; i < tiles.length; i++) {
        ctx.drawImage(tiles[i], (i % cols) * POST_W, Math.floor(i / cols) * POST_H);
    }
    return canvas;
}

function showToast(msg, success = false) {
    toast.textContent = msg;
    toast.className = 'toast show' + (success ? ' success' : '');
    setTimeout(() => toast.classList.remove('show'), 3000);
}
