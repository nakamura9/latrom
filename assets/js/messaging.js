import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {convertToRaw} from 'draft-js';

import ChatRoot from '../js/messaging/container/chat_root';
import GroupChatRoot from '../js/messaging/container/group_root';
import EmailEditor from '../js/messaging/container/rich_text';
import InboxView from '../js/messaging/container/inbox';
import MultipleSelectWidget from '../js/src/multiple_select/containers/root';

const rich_text = document.getElementById('message-field');
const group_participants_widget = document.getElementById('group-participant-select')
const threadView = document.getElementById('thread-widget');
const groupThreadView = document.getElementById('group-widget');
const inboxContainer = document.getElementById('inbox-widget');


if(threadView){
    ReactDOM.render(<ChatRoot />, threadView);
}else if(groupThreadView){
    ReactDOM.render(<GroupChatRoot />, groupThreadView);
}else if(rich_text){
    ReactDOM.render(<EmailEditor textHandler={(state) =>{
            const contentState = state.editorState.getCurrentContent();
            const data = encodeURIComponent(
                JSON.stringify(convertToRaw(contentState))
              );
            let field = document.getElementById('id_body');
            field.setAttribute('value', data);
    }}/>, rich_text);

}else if(group_participants_widget){
    ReactDOM.render(<MultipleSelectWidget 
        inputField="participants"
        dataURL="/base/api/users/"
        nameField="username"/>, group_participants_widget)
}else if(inboxContainer){
    ReactDOM.render(<InboxView />, inboxContainer)
}