let form = document.querySelector(".url-form");
var timesRun = 0;
    
form.addEventListener("submit", function (e) {

    e.preventDefault();
    let formdata = new FormData(this);
    let input = formdata.get("url-input");
    const API_URL =  document.URL + "/airbnb-API?url=" + `${encodeURIComponent(input)}`;
    const LOADING = $(".loading");
    LOADING.removeClass("hidden");
    
    async function getJSON() {
        const RESPONSE = await fetch(API_URL);
        var JSON = await RESPONSE.json();
        LOADING.addClass("hidden");
        var divClass = 'airbnb' + timesRun.toString();
        const LEFT_DIV = '<div class = "left ' + divClass + '-left"></div>';
        const RIGHT_DIV = '<div class = "right ' + divClass + '-right"></div>';
        $('.searches').prepend('<div class = "airbnb ' + divClass + '"><div class = "info ' + divClass + '-info">' + LEFT_DIV + RIGHT_DIV + '</div>');

        if (JSON.hasOwnProperty('stay price')){
            $('.' + divClass).prepend('<h5 class = "price"> $' + JSON['stay price'] + ' per night</h5>');
            $('.' + divClass + '-info').addClass("underline");
            delete JSON['stay price'];
        }

        if (JSON.hasOwnProperty('Airbnb info')){
            $('.' + divClass).prepend('<h5 class = "">' + JSON['Airbnb info'] + '</h5>');
            delete JSON['Airbnb info'];
        }

        if (JSON.hasOwnProperty('Airbnb link') && JSON.hasOwnProperty('Airbnb name') ) {
            $('.' + divClass).prepend('<a href = "' + JSON['Airbnb link'] + '" target="_blank" class = "airbnb-pic">' + JSON['Airbnb name'] + '</a>');
            delete JSON['Airbnb link'];
            delete JSON['Airbnb name'];
        }

        if (JSON.hasOwnProperty('Airbnb picture')) {
            $('.' + divClass + '-left').append('<picture> <img src = "' + JSON['Airbnb picture'] +'"> </picture>');
            delete JSON['Airbnb picture'];
        }

        for (var key in JSON){
            $('.' + divClass + '-right').append('<p>' + key + ": " + JSON[key] + '</p>');
        }
    }

    getJSON();
    timesRun++;
         
    });