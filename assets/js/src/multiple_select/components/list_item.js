import React from 'react';

const selectedItem = (props) =>{
    const buttonStyle = {
        color: "red",
        backgroundColor: "white",
        border: "0px"
    };

    const containerStyle = {
        width: "100%",
        height: "30px",
        padding: "0px 5px",
        border: "1px solid #007bff",
        backgroundColor: "white"
    };

    return(
        <div style={containerStyle}>{props.value}
            <span style={{float: "right"}}>
                <button 
                    style={buttonStyle} 
                    onClick={() => props.removeHandler(props.index)}
                    type="button">
                    <i className="fas fa-times"></i>
                </button>
            </span>
        </div>
    )
}

export default selectedItem;