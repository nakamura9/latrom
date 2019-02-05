function setMultipleAttrs(element, obj){
    for(var key in obj){
        element.setAttribute(key, obj[key]);
    }
}

function setDataPayload(data){
    //takes an object and a csrfmiddlewaretoken as arguments
    let payload = new FormData();
    for(var key in data){
        payload.set(key, data[key]);
    }
    return payload;
}


export default setMultipleAttrs;

export {setDataPayload};
