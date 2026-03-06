let mediaRecorder;
let audioChunks = [];

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                document.getElementById("audioPlayer").src = audioUrl;

                window.recordedBlob = audioBlob;
            };
        });
}

function stopRecording() {
    mediaRecorder.stop();
}

function uploadRecording() {
    if (!window.recordedBlob) {
        alert("Record audio first!");
        return;
    }

    let formData = new FormData();
    formData.append("audio", window.recordedBlob, "recording.wav");

    fetch("/dashboard", {
        method: "POST",
        body: formData
    })
    .then(() => {
        alert("Recording uploaded!");
        location.reload();
    });
}