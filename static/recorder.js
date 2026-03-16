let mediaRecorder;
let audioChunks = [];

function getBestMimeType() {
    // Prefer formats Whisper handles well after ffmpeg conversion
    const types = [
        'audio/webm;codecs=pcm',   // Best quality, raw PCM in webm
        'audio/webm;codecs=opus',  // Standard webm opus
        'audio/webm',              // Generic webm
        'audio/ogg;codecs=opus',   // Ogg opus fallback
        'audio/mp4',               // Safari fallback
    ];
    for (const type of types) {
        if (MediaRecorder.isTypeSupported(type)) {
            console.log('[Recorder] Using MIME type:', type);
            return type;
        }
    }
    console.warn('[Recorder] No preferred MIME type supported, using browser default');
    return '';
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ 
        audio: {
            channelCount: 1,        // Force mono — matches Whisper's expectation
            sampleRate: 16000,      // 16kHz — Whisper's native sample rate
            echoCancellation: true,
            noiseSuppression: true,
        }
    })
    .then(stream => {
        audioChunks = [];
        window.recordedBlob = null;

        const mimeType = getBestMimeType();
        const options = mimeType ? { mimeType } : {};

        mediaRecorder = new MediaRecorder(stream, options);

        mediaRecorder.ondataavailable = event => {
            if (event.data && event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            // Stop all tracks to release mic
            stream.getTracks().forEach(track => track.stop());

            const mimeUsed = mediaRecorder.mimeType || 'audio/webm';
            const audioBlob = new Blob(audioChunks, { type: mimeUsed });

            console.log('[Recorder] Blob size:', audioBlob.size, 'bytes, type:', mimeUsed);

            if (audioBlob.size < 1000) {
                alert("Recording seems too short or empty. Please try again.");
                return;
            }

            const audioUrl = URL.createObjectURL(audioBlob);
            document.getElementById("audioPlayer").src = audioUrl;
            window.recordedBlob = audioBlob;
            window.recordedMime = mimeUsed;
        };

        // Collect data every 250ms so we don't lose audio at the end
        mediaRecorder.start(250);

        console.log('[Recorder] Recording started');
        document.getElementById("btnStart").disabled = true;
        document.getElementById("btnStop").disabled = false;
    })
    .catch(err => {
        console.error('[Recorder] Mic access error:', err);
        alert("Could not access microphone: " + err.message);
    });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        console.log('[Recorder] Recording stopped');
    }
    document.getElementById("btnStart").disabled = false;
    document.getElementById("btnStop").disabled = true;
}

function uploadRecording() {
    if (!window.recordedBlob) {
        alert("Please record audio first!");
        return;
    }

    if (window.recordedBlob.size < 1000) {
        alert("Recording is too small. Please record again.");
        return;
    }

    // Show loading overlay
    document.getElementById("loadingOverlay").style.display = "flex";

    // Determine file extension from mime type
    const mime = window.recordedMime || 'audio/webm';
    let ext = '.webm';
    if (mime.includes('ogg')) ext = '.ogg';
    else if (mime.includes('mp4')) ext = '.mp4';

    const filename = `recording${ext}`;
    console.log('[Recorder] Uploading as:', filename, '| size:', window.recordedBlob.size);

    let formData = new FormData();
    formData.append("audio", window.recordedBlob, filename);

    fetch("/dashboard", {
        method: "POST",
        body: formData
    })
    .then(async response => {
        if (!response.ok) {
            const text = await response.text();
            console.error('[Recorder] Server error:', text);
            alert("Upload failed with status: " + response.status);
        } else {
            location.reload();
        }
    })
    .catch(error => {
        console.error('[Recorder] Fetch error:', error);
        alert("Upload failed: " + error);
    })
    .finally(() => {
        document.getElementById("loadingOverlay").style.display = "none";
    });
}