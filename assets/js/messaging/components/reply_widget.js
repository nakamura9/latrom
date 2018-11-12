import React from 'react';
import $ from 'jquery';

const ReplyWidget = (props) =>{
    
        return(
            <div>
                <form method="post" action={`/messaging/reply-message/${props.msgID}`}>
                    <textarea 
                        className="form-control"  
                        cols="30" 
                        rows="10"
                        name="reply">
                    </textarea>
                    <input 
                        type="hidden" 
                        name="csrfmiddlewaretoken"
                        value={`${$("input[name='csrfmiddlewaretoken']").val()}`} />
                    <input className="button" type="submit" value="Send" />
                </form>
            </div>
        )
    
}

export default ReplyWidget;