import React from 'react';

const chatInput = (props) =>{
    return(
        <div>
            <div className="input-group">
                <textarea 
                    autoFocus
                    className="form-control"
                    rows={2} 
                    style={{
                        border: "1px solid #007bff",
                        width: "80%",
                        resize: 'none'
                    }} 
                    value={props.inputText}
                    onChange={props.inputHandler}/>
            <div className="input-group-append">
                <button 
                    style={{
                        color: "white",
                        backgroundColor: "#07f",
                        border:"0px",
                        height: '64px',

                    }}
                    onClick={props.sendMessage}> <b style={{
                        fontSize: "16pt"
                    }}></b> <i className="fas fa-feather-alt" style={{"fontSize":"2.5rem", "padding": "5px"}}></i></button>
            </div>
            </div>
        </div>
    
    )
}

export default chatInput;