const urlParams = new URLSearchParams(window.location.search);
const id = urlParams.get("id");

const activitiesOl = document.querySelector('.activities ol');

const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

const activities = JSON.parse(document.getElementById("activitiesJson").textContent);

function dateFromIsoString(string) {
    const date = new Date();
    date.setTime(Date.parse(string));
    return date;
}

// We definitely should have used some frontend framework.
function redrawActivities() {
    while (activitiesOl.firstChild) {
        activitiesOl.firstChild.remove();
    }

    for (const activity of activities) {
        const li = document.createElement('div');
        li.classList.add('activity');

        const startTimeDiv = document.createElement('div');
        startTimeDiv.innerText = `Start: ${dateFromIsoString(activity.start_time)}`;

        const endTimeDiv = document.createElement('div');
        endTimeDiv.innerText = `End: ${dateFromIsoString(activity.end_time)}`;

        const noteDiv = document.createElement('div');
        noteDiv.innerText = activity.note;
        noteDiv.contentEditable = 'true';
        noteDiv.addEventListener('keydown', function(event) {
            if(event.keyCode !== 13) {
                return;
            }
            event.preventDefault();
            
            api.updatePlanActivity(id, activity.id, {
                note: event.target.innerText,
            })
            .then((response) => {
                const div = document.createElement("div");
                div.classList.add('function');
                div.innerText = response['message'];

                chatMessages.appendChild(div);
                
                requestAnimationFrame(() => chatMessages.scrollTo(0, chatMessages.scrollHeight));
            })
            .catch((error) => {
                alert(error);
            });
        });

        const activityImg = document.createElement('img');
        activityImg.src = activity.link;

        li.appendChild(startTimeDiv);
        li.appendChild(endTimeDiv);
        li.appendChild(noteDiv);
        li.appendChild(activityImg);

        activitiesOl.appendChild(li);
    }
}

redrawActivities();

chatInput.addEventListener("keydown", function (event) {
    if (event.keyCode !== 13) {
        return;
    }

    const value = chatInput.value;
    chatInput.value = "";

    api
    .chat(id, value)
    .then(function (response) {
        const userMessageDiv = document.createElement("div");
        userMessageDiv.classList.add("user");
        userMessageDiv.innerText = value;
        chatMessages.appendChild(userMessageDiv);

        for (const message of response.messages) {
            const div = document.createElement("div");
            div.classList.add(message.role);
            div.innerText = message.content;

            chatMessages.appendChild(div);
        }

        if (response.activities.created !== null) {
            activities.push(response.activities.created);
            activities.sort((a, b) => {
                return dateFromIsoString(a.start_time) - dateFromIsoString(b.start_time);
            });
        }

        if (response.activities.deleted !== null) {
            const index = activities.findIndex((a) => a.id === response.activities.deleted);
            activities.splice(index, 1);

            // TODO: Is this needed? I don't think so?
            /*
            activities.sort((a, b) => {
            return dateFromIsoString(a.start_time) - dateFromIsoString(b.start_time);
            });
             */
        }

        if (response.activities.modified !== null) {
            const index = activities.findIndex((a) => a.id === response.activities.modified.id);
            activities[index] = response.activities.modified;

            activities.sort((a, b) => {
                return dateFromIsoString(a.start_time) - dateFromIsoString(b.start_time);
            });
        }

        // TODO: Add Activities dirty flag
        redrawActivities();

        // TODO: Is there an event I can use for this?
        // Is this correct?
        requestAnimationFrame(() =>
            chatMessages.scrollTo(0, chatMessages.scrollHeight));
    })
    .catch(function (error) {
        alert(error);
    });
});

window.addEventListener("load", () => {
    chatMessages.scrollTo(0, chatMessages.scrollHeight);
});
