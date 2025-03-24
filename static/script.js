document.addEventListener('DOMContentLoaded', function() {
  const encryptBtn = document.getElementById('encrypt-btn');
  const decryptBtn = document.getElementById('decrypt-btn');
  const resultDiv = document.getElementById('result');
  const fileInput = document.getElementById('file');
  const passwordInput = document.getElementById('password');

  encryptBtn.addEventListener('click', function() {
      const file = fileInput.files[0];
      const password = passwordInput.value;

      if (!file || !password) {
          resultDiv.innerHTML = 'Please select a file and enter a password.';
          return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('password', password);

      fetch('/encrypt', {
          method: 'POST',
          body: formData
      })
      .then(response => response.json())
      .then(data => {
          if (data.error) {
              resultDiv.innerHTML = `Error: ${data.error}`;
          } else {
              resultDiv.innerHTML = `File encrypted successfully! Download it from <a href="${data.encrypted_file_path}" target="_blank">${data.encrypted_file_path}</a>`;
          }
      })
      .catch(error => {
          resultDiv.innerHTML = `Error: ${error.message}`;
      });
  });

  decryptBtn.addEventListener('click', function() {
      const file = fileInput.files[0];
      const password = passwordInput.value;

      if (!file || !password) {
          resultDiv.innerHTML = 'Please select a file and enter a password.';
          return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('password', password);

      fetch('/decrypt', {
          method: 'POST',
          body: formData
      })
      .then(response => response.blob())
      .then(blob => {
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = file.name.replace(".enc", ""); // To suggest the original name for download
          link.click();
      })
      .catch(error => {
          resultDiv.innerHTML = `Error: ${error.message}`;
      });
  });
});