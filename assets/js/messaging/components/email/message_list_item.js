import React from 'react';

const listItem = (props) =>{
    let classNames = ['list-group-item'];
    if(props.current === props.msg.id){
        classNames.push('selected-message');
    }
    if(!props.msg.read){
        classNames.push('unread-message');
    }
    return (
        <li onClick={ () => props.setCurrent(props.msg.id, props.listIndex)} 
            className={classNames.join(' ')}>
            <h6>{props.msg.sent_from}</h6>
            <p>{props.msg.subject.substring(0, 25)}
                <span>{props.msg.subject.length > 25 ? '...' : '' }</span>
            </p>
        </li>
    )
}

export default listItem;