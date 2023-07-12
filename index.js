

let form = document.querySelector(".url-form");
    
            form.addEventListener("submit", function (e) {
            e.preventDefault()
            
            let formdata = new FormData(this);
            let input = formdata.get("url-input");
            let url = window.location.href

            alert(url);

            });