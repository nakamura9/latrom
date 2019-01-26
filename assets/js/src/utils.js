function setMultipleAttrs(element, obj){
    for(var key in obj){
        element.setAttribute(key, obj[key]);
    }
}

export default setMultipleAttrs;