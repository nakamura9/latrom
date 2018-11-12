import React from 'react';

const ReplyWidget = (props) =>{
    
        return(
            <div>
                <textarea 
                    className="form-control"  
                    cols="30" 
                    rows="10"
                    name="reply"
                    value={props.value}
                    onChange={props.inputHandler}
                    >
                </textarea>
                <button 
                    className="btn btn-primary" 
                    style={{float: "right"}}
                    onClick={props.clickHandler}>
                Send <i className="fas fa-angle-double-right"></i>
                </button>
            </div>
        )
    
}

export default ReplyWidget;