import React from 'react';
import styles from './chatStyles.css';


const MessageBubble = (props) =>{
    console.log(props.message)
    return(
        <div className={styles.bubble} style={{
            backgroundColor: props.isSender ? "#05f" : "#0cf",
            float: props.isSender ? 'left' : 'right'
        }} id={`${props.MessageID}`}>
            {props.showSender && !props.isSender ?
                <p>{props.message.sender.username}</p>
            : null}    
        
            <p>{props.message.message_text}<br /><span style={{
                float: "right",
                color: "#ddd"
            }}>{props.created}</span></p>
            
        </div>
    )
}

export default MessageBubble;