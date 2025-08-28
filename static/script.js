const socket = io();

function gerarRelatorio(event) {
    event.preventDefault();
    const cod = document.getElementById("airport").value;
    document.getElementById("status").innerText = "🔄 Iniciando...";
    document.getElementById("relatorio").innerText = "";
    socket.emit("generate_report", { code: cod });
}

socket.on("message", data => {
    if(data.type == 'success'){
        document.getElementById("relatorio").innerHTML = data.text;
    }else{
        setStatus(data.text, data.type)
    }
});

function setStatus(texto, tipo) {
    const statusEl = document.getElementById("status");
    statusEl.innerText = texto;
  
    statusEl.classList.remove("status-alert", "status-error");
  
    if (tipo === "alert") {
        statusEl.classList.add("status-alert");
    } else if (tipo === "error") {
        statusEl.classList.add("status-error");
    }
  }