import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {convertToRaw} from 'draft-js';

import ChatRoot from '../js/messaging/container/chat_root';
import GroupChatRoot from '../js/messaging/container/group_root';
import EmailEditor from '../js/messaging/container/rich_text';
import InboxView from '../js/messaging/container/inbox';
import MultipleSelectWidget from '../js/src/multiple_select/containers/root';
import SearchableWidget from '../js/src/components/searchable_widget';

const rich_text = document.getElementById('message-field');
const group_participants_widget = document.getElementById('group-participant-select')
const threadView = document.getElementById('thread-widget');
const groupThreadView = document.getElementById('group-widget');
const inboxContainer = document.getElementById('inbox-widget');
const toWidget = document.getElementById('email-to')
const ccWidget = document.getElementById('email-cc')
const bccWidget = document.getElementById('email-bcc')


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


if(toWidget){
    ReactDOM.render(<SearchableWidget 
                        newLink="/messaging/create-email-address"
                        dataURL="/messaging/api/email-address"
                        displayField="address"
                        onSelect={(value) => {
                            document.getElementById('id_to').value = value;
                        }}
                        onClear={() =>{
                            document.getElementById('id_to').value = "";
                        }}
                        idField="id"/>, toWidget)
    ReactDOM.render(<MultipleSelectWidget
                        inputField="copy"
                        dataURL="/messaging/api/email-address"
                        nameField="address"
                        /*resProcessor={(res) =>{
                            return res.data.map((emailaddr) => )
                        }}*/ />, ccWidget)
    ReactDOM.render(<MultipleSelectWidget
                        inputField="blind_carbon_copy"
                        dataURL="/messaging/api/email-address"
                        nameField="address"
                         />, bccWidget)
}