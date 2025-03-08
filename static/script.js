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
  errorDiv.style.visibility = "hidden";
};

const getFile = () => {
  const pass = document.getElementById("password");
  const password = pass.value;
  if (password === "") {
    const error = document.getElementById("message");
    error.innerHTML = "Please enter a password";
    const errorDiv = document.getElementById("error");
    errorDiv.style.visibility = "visible";
    return;
  }
  if (fileType === null) {
    const error = document.getElementById("message");
    error.innerHTML = "Please upload a file";
    const errorDiv = document.getElementById("error");
    errorDiv.style.visibility = "visible";
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
        console.log(data);
        const downloadFile = document.createElement("a");
        const fileURL = URL.createObjectURL(data);
        downloadFile.href = fileURL;
        const fileName = formData.get("file")?.name || "encrypted-file";
        downloadFile.download = fileName + ".enc";
        downloadFile.click();
        URL.revokeObjectURL(fileURL);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        window.location.reload();
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
        console.error(err);
      })
      .finally(() => {
        window.location.reload();
      });
  }
  
};
