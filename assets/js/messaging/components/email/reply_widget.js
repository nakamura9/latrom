import React from 'react';
import EmailEditor from '../../container/rich_text';
import {convertToRaw} from 'draft-js';

const ReplyWidget = (props) =>{
    
        return(
            <div>
                <EmailEditor textHandler={(state) =>{
                    const contentState = state.editorState.getCurrentContent();
                    const data = convertToRaw(contentState);
                    props.setReply(data)
                }}/>
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