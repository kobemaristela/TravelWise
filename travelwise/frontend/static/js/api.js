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
    
    window.api.getCsrfToken = function() {
        const csrfToken = getCookie('csrftoken');
        
        if(csrfToken === null) {
            throw new Error('Missing cookie with name "csrftoken"');
        }
        
        return csrfToken;
    };
    
    window.api.chat = async function(planId, message) {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken(),
                'Content-Type': 'application/json; charset=utf-8',
            },
            body: JSON.stringify({
                'planId': Number(planId),
                'message': message,
            }),
        });
        
        const json = await response.json();
        
        if(!response.ok) {
            // TODO: Make Error
            throw json;
        }
        
        return json;
    };
    
    window.api.updatePlanActivity = async function(planId, activityId, patch = {}) {
        const response = await fetch(`/api/plan/${planId}/activity/${activityId}`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': this.getCsrfToken(),
                'Content-Type': 'application/json; charset=utf-8',
            },
            body: JSON.stringify(patch),
        });
        
        const json = await response.json();
        if(!response.ok) {
            // TODO: Make Error
            throw json;
        }
        return json;
    };
})();