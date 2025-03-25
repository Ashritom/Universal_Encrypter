document.addEventListener("DOMContentLoaded", function () {
  const modeToggle = document.getElementById("mode-toggle");
  const encryptLabel = document.querySelector(".encrypt-label");
  const decryptLabel = document.querySelector(".decrypt-label");
  const actionBtn = document.getElementById("action-btn");
  const actionText = document.getElementById("action-text");
  const resultDiv = document.getElementById("result");
  const fileInput = document.getElementById("file");
  const fileInfo = document.getElementById("file-info");
  const passwordInput = document.getElementById("password");
  const togglePasswordBtn = document.getElementById("toggle-password");
  const progressContainer = document.getElementById("progress-container");
  const progressBar = document.getElementById("progress-bar");
  const passwordStrengthMeter = document.getElementById(
    "password-strength-meter"
  );

  let currentMode = "encrypt";

  function updateModeUI(mode) {
    currentMode = mode;
    fileInput.value = "";
    fileInfo.textContent = "No file selected";
    if (mode === "encrypt") {
      encryptLabel.classList.add("active");
      decryptLabel.classList.remove("active");
      actionBtn.textContent = "Encrypt File";
      actionText.textContent = "Encrypt";
      actionBtn.className = "action-btn encrypt-action";
      progressBar.className = "encrypt-progress";
    } else {
      encryptLabel.classList.remove("active");
      decryptLabel.classList.add("active");
      actionBtn.textContent = "Decrypt File";
      actionText.textContent = "Decrypt";
      actionBtn.className = "action-btn decrypt-action";
      progressBar.className = "decrypt-progress";
    }
  }

  modeToggle.addEventListener("change", function () {
    updateModeUI(this.checked ? "decrypt" : "encrypt");
  });

  fileInput.addEventListener("change", function () {
    if (this.files.length > 0) {
      const fileName = this.files[0].name;
      const fileSize = (this.files[0].size / 1024).toFixed(2);
      fileInfo.textContent = `${fileName} (${fileSize} KB)`;
      fileInfo.style.color = "#8a8b8b";
    } else {
      fileInfo.textContent = "No file selected";
      fileInfo.style.color = "#8a8b8b";
    }
  });

  togglePasswordBtn.addEventListener("click", function () {
    const type =
      passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);
    this.textContent = type === "password" ? "👁️" : "🔒";
  });

  function checkPasswordStrength(password) {
    let strength = 0;

    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[a-z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 12.5;
    if (/[^A-Za-z0-9]/.test(password)) strength += 12.5;

    return strength;
  }

  passwordInput.addEventListener("input", function () {
    const password = this.value;
    const strength = checkPasswordStrength(password);

    passwordStrengthMeter.style.width = `${strength}%`;

    if (strength < 25) {
      passwordStrengthMeter.style.backgroundColor = "#e74c3c";
    } else if (strength < 50) {
      passwordStrengthMeter.style.backgroundColor = "#f39c12";
    } else if (strength < 75) {
      passwordStrengthMeter.style.backgroundColor = "#f1c40f";
    } else {
      passwordStrengthMeter.style.backgroundColor = "#2ecc71";
    }
  });

  function showProgress() {
    progressContainer.style.display = "block";
    progressBar.style.width = "0%";
    let width = 0;

    const interval = setInterval(() => {
      if (width >= 90) {
        clearInterval(interval);
      } else {
        width += 5;
        progressBar.style.width = width + "%";
      }
    }, 150);

    return interval;
  }

  function completeProgress(interval) {
    clearInterval(interval);
    progressBar.style.width = "100%";
    setTimeout(() => {
      progressContainer.style.display = "none";
    }, 1000);
  }

  function showResult(content, isError = false) {
    resultDiv.innerHTML = content;
    resultDiv.className = isError ? "result-card error-card" : "result-card";
    resultDiv.classList.add("show");
    resultDiv.style.display = "block";
    resultDiv.classList.add("animate-in");
  }

  actionBtn.addEventListener("click", function () {
    const file = fileInput.files[0];
    const password = passwordInput.value;

    if (!file) {
      showResult('<div class="error">Please select a file.</div>', true);
      return;
    }

    if (!password) {
      showResult('<div class="error">Please enter a password.</div>', true);
      return;
    }

    if (currentMode === "encrypt") {
      const passwordStrength = checkPasswordStrength(password);
      if (passwordStrength < 100) {
        showResult(
          '<div class="error">Your password does not meet security requirements.</div>',
          true
        );
        return;
      }
    }

    resultDiv.innerHTML = "";
    const progressInterval = showProgress();

    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    if (currentMode === "encrypt") {
      fetch("/encrypt", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          completeProgress(progressInterval);
          passwordInput.value = "";
          passwordStrengthMeter.style.width = "0%";
          if (data.error) {
            showResult(`<div class="error">Error: ${data.error}</div>`, true);
          } else {
            showResult(`
              <div class="success">File encrypted successfully!</div>
              <p style="margin-top: 15px;">Download your encrypted file:</p>
              <a href="${data.encrypted_file_path}" class="download-link" download>
                <button class="action-btn encrypt-action" style="margin-top: 10px;">
                  Download Encrypted File
                </button>
              </a>
            `);
          }
        })
        .catch((error) => {
          completeProgress(progressInterval);
          showResult(`<div class="error">Error: ${error.message}</div>`, true);
        });
    } else {
      fetch("/decrypt", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          completeProgress(progressInterval);
          passwordInput.value = "";
          passwordStrengthMeter.style.width = "0%";
          if (
            !response.ok &&
            response.headers.get("content-type")?.includes("application/json")
          ) {
            return response.json().then((err) => {
              throw new Error(err.error || "Decryption failed");
            });
          }
          return response.blob();
        })
        .then((blob) => {
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = file.name.replace(".enc", "");
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          showResult('<div class="success">File decrypted successfully!</div>');
        })
        .catch((error) => {
          showResult(`<div class="error">${error.message}</div>`, true);
        });
    }
  });

  updateModeUI("encrypt");
});