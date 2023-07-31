(function() {
    function getCookie(name) {
        const cookie = decodeURIComponent(document.cookie);
        const parts = cookie.split(';');
        const prefix = name + '=';
        
        for(let i = 0; i < parts.length; i++) {
            if(parts[i].startsWith(prefix)) {
                return parts[i].substring(prefix.length);
            }
        }
        
        return null;
    }
    
    window.api = {};
    
    window.api.chat = function(planId, message) {
        const csrftoken = getCookie('csrftoken');
        
        if(csrftoken === null) {
            throw new Error('Missing cookies with name "csrftoken"');
        }
        
        return fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json; charset=utf-8',
            },
            body: JSON.stringify({
                'planId': planId,
                'message': message,
            }),
        }).then(function (response) {
            return response.json();
        });
    };
})();