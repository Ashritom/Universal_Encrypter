<<<<<<< HEAD
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
=======
let fileType = null;

const displayFileEncrypt = (event) => {
  const filename = document.getElementById("filenameE");
  const file = event.target.files[0];
  filename.innerHTML = file ? file.name : "No file selected";
  fileType = "encrypt";
};

const displayFileDecrypt = (event) => {
  const filename = document.getElementById("filenameD");
  const file = event.target.files[0];
  filename.innerHTML = file ? file.name : "No file selected";
  fileType = "decrypt";
};

const closeError = () => {
  const errorDiv = document.getElementById("error");
  errorDiv.classList.remove("show");
};

const showError = (messageText) => {
  const message = document.getElementById("message");
  message.innerHTML = messageText;
  const errorDiv = document.getElementById("error");
  errorDiv.classList.add("show");
};

const getFile = (type) => {
  let pass = document.getElementById("passwordD");
  if (type == "Encrypt") {
    pass = document.getElementById("passwordE");
  }
  const password = pass.value;
  if (password === "") {
    showError("Please enter a password");
    return;
  }
  if (fileType === null) {
    showError("Please upload a file");
    return;
  } else if (fileType === "encrypt") {
    const file = document.getElementById("encrypt").files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    fetch("/encrypt", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.blob())
      .then((data) => {
        const downloadFile = document.createElement("a");
        const fileURL = URL.createObjectURL(data);
        downloadFile.href = fileURL;
        const fileName = formData.get("file")?.name || "encrypted-file";
        downloadFile.download = fileName + ".enc";
        downloadFile.click();
        URL.revokeObjectURL(fileURL);
      })
      .catch((err) => {
        showError("Error encrypting file");
        console.error(err);
      })
      .finally(() => {
        pass.value = "";
        document.getElementById("filenameE").innerHTML = "No file selected";
        document.getElementById("encrypt").value = "";
        fileType = null;
      });
  } else if (fileType === "decrypt") {
    const file = document.getElementById("decrypt").files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    fetch("/decrypt", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.blob())
      .then((data) => {
        const downloadFile = document.createElement("a");
        const fileURL = URL.createObjectURL(data);
        downloadFile.href = fileURL;
        downloadFile.download = file.name.replace(".enc", "");
        downloadFile.click();
      })
      .catch((err) => {
        showError("Error decrypting file");
        console.error(err);
      })
      .finally(() => {
        pass.value = "";
        document.getElementById("filenameD").innerHTML = "No file selected";
        document.getElementById("decrypt").value = "";
        fileType = null;
      });
  }
};
>>>>>>> 15a6432cc96cdb22f5e4e3471dfd573879738748
