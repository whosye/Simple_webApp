
document.getElementById('fetchHello').addEventListener('click', function () {
    fetch('/hello')  
        .then(response => response.json())  
        .then(data => {
            document.getElementById('messageContainer').textContent = data.message;
        })
        .catch(error => {
            console.error(error);
        });
});