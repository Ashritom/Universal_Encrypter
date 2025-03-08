document.getElementById('encrypt-btn').addEventListener('click', function() {
    handleFileAction('encrypt');
});

document.getElementById('decrypt-btn').addEventListener('click', function() {
    handleFileAction('decrypt');
});



function handleFileAction(action) {
    const fileInput = document.getElementById('file');
    const passwordInput = document.getElementById('password');
    const file = fileInput.files[0];
    const ext = file.name.split('.')[1];
    const password = passwordInput.value;

    if (!file || !password) {
        alert("Please select a file and enter a password.");
        return;
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    // Show progress bar
    document.getElementById('progress-container').style.display = 'block';

    fetch(`/${action}`, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('File not found');
    })  // Parse the JSON response
    .then(data => {
        console.log(data);
        const url = window.URL.createObjectURL(data);
        const a = document.createElement('a');
        a.style.display = null;
        a.href = url;
        if (action == "encrypt"){
            a.download = `encrypted.${ext}.enc`;
        }
        else{
            a.download = `decrypted.${ext}`;
        }
        a.click();

        // Display message (success or error)
        // document.getElementById('result').textContent = data.message || data.error;

        // // Handle the download link creation
        // if (data.encrypted_file_path) {
        //     const encryptedFileLink = document.createElement('a');
        //     encryptedFileLink.href = data.encrypted_file_path;  // Should be a URL like '/uploads/file.enc'
        //     encryptedFileLink.download = data.encrypted_file_path.split('/').pop();  // Extract filename
        //     encryptedFileLink.textContent = "Download the encrypted file";
        //     document.getElementById('result').appendChild(encryptedFileLink);
        // } else if (data.decrypted_file_path) {
        //     const decryptedFileLink = document.createElement('a');
        //     decryptedFileLink.href = data.decrypted_file_path;  // Should be a URL like '/uploads/file'
        //     decryptedFileLink.download = data.decrypted_file_path.split('/').pop();  // Extract filename
        //     decryptedFileLink.textContent = "Download the decrypted file";
        //     document.getElementById('result').appendChild(decryptedFileLink);
        // }
    })
    .catch(error => {
        console.error(error);
        document.getElementById('result').textContent = "An error occurred. Please try again.";
    })
    .finally(() => {
        // Hide progress bar
        document.getElementById('progress-container').style.display = 'none';
    });
}