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
