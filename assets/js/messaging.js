import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {convertToRaw} from 'draft-js';

import ChatRoot from '../js/messaging/container/chat_root';
import GroupChatRoot from '../js/messaging/container/group_root';
import EmailEditor from '../js/messaging/container/rich_text';
import InboxView from '../js/messaging/container/inbox';
import MultipleSelectWidget from '../js/src/multiple_select/containers/root';
import SearchableWidget from '../js/src/components/searchable_widget';
import FilePicker from '../js/src/components/custom_file_picker';

const rich_text = document.getElementById('message-field');
const group_participants_widget = document.getElementById('group-participant-select')
const threadView = document.getElementById('thread-widget');
const groupThreadView = document.getElementById('group-widget');
const inboxContainer = document.getElementById('inbox-widget');
const toWidget = document.getElementById('email-to')
const ccWidget = document.getElementById('email-cc')
const bccWidget = document.getElementById('email-bcc')
const attachmentWidget = document.getElementById('email-attachment')

if(threadView){
    ReactDOM.render(<ChatRoot />, threadView);
}else if(groupThreadView){
    ReactDOM.render(<GroupChatRoot />, groupThreadView);
}else if(group_participants_widget){
    ReactDOM.render(<MultipleSelectWidget 
        inputField="participants"
        dataURL="/base/api/users/"
        nameField="username"/>, group_participants_widget)
}else if(inboxContainer){
    ReactDOM.render(<InboxView />, inboxContainer)
}else if(toWidget){
    //get page url
    const url = window.location.href;
    let prePopulatedURL = null;
    if(url.indexOf('update-draft') !== -1){
        const splitURL = url.split('/');
        const pk = splitURL[splitURL.length -1]
        prePopulatedURL = '/messaging/api/email/' + pk;
    }
    
    const toprePopulatedHandler = (data) =>{
        return data.to
    }
    
    ReactDOM.render(<SearchableWidget
                        prePopulatedURL={prePopulatedURL}
                        prePopulationHandler={toprePopulatedHandler} 
                        newLink="/messaging/create-email-address"
                        dataURL="/messaging/api/email-address"
                        displayField="address"
                        widgetID="to"
                        onSelect={(value) => {
                            document.getElementById('id_to').value = value;
                        }}
                        onClear={() =>{
                            document.getElementById('id_to').value = "";
                        }}
                        idField="id"/>, toWidget)
    ReactDOM.render(<MultipleSelectWidget
                        populatedURL={prePopulatedURL}
                        resProcessor={(res) => res.data.copy}
                        inputField="copy"
                        dataURL="/messaging/api/email-address"
                        newLink='/messaging/create-email-address'
                        nameField="address"
                        /*resProcessor={(res) =>{
                            return res.data.map((emailaddr) => )
                        }}*/ />, ccWidget)


    ReactDOM.render(<MultipleSelectWidget
                        inputField="blind_carbon_copy"
                        populatedURL={prePopulatedURL}
                        resProcessor={(res) => res.data.blind_copy}
                        dataURL="/messaging/api/email-address"
                        nameField="address"
                        newLink='/messaging/create-email-address'
                         />, bccWidget)
    ReactDOM.render(<EmailEditor 
                        prePopulatedURL={prePopulatedURL}
                        textHandler={(state) =>{
                        const contentState = state.editorState.getCurrentContent();
                        const data = encodeURIComponent(
                            JSON.stringify(convertToRaw(contentState))
                            );
                        let field = document.getElementById('id_body');
                        field.setAttribute('value', data);
                        }}/>, rich_text);
    // add support for getting initial 
    if(!prePopulatedURL){
        ReactDOM.render(<FilePicker
            fieldName="attachment"
            fieldID="id_attachment" />, attachmentWidget)
    }
    /**/
}