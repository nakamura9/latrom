import React, {Component} from 'react';
import axios from 'axios';
import ChatWidget from '../components/chat/chat';
import {Aux} from '../../src/common';
import ChatHeader from '../components/chat/chat_header';

export default class ChatRoot extends Component{
    constructor(props){
        super(props)
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];
        this.state = {
            messages: [],
            currentMessage: null,
            currentUser: null,
            chatPk: pk,
        }    
    }
    

    setCurrentMessage = (msg) =>{
        this.setState({currentMessage: msg})
    }

    componentDidMount(){
        this.intervalID = null;

        //get the message that provides its thread
        axios({
            'method': 'GET',
            'url': '/base/api/current-user'
        }).then(res => {
            this.setState({currentUser: {
                name: res.data.name,
                id: res.data.pk
            },
        })
        })
        this.intervalID = setInterval(this.getMessages, 3000);

        this.getMessages()
    }
    getMessages =() =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/chat/' + this.state.chatPk
        }).then( res => {
            this.setState({
                messages: res.data.messages,
                currentMessage: res.data.messages[res.data.messages.length - 1],
                receiver: res.data.receiver
            })
        })
    }
    

    attachmentHandler = (evt) =>{
        const file = evt.target.files[0];
        const extension = file.name.split('.')[1];

        if(file.size > 5000000){
            alert('Cannot Upload files larger than 5MB');
            return;
        }else if(!['jpg', 'jpeg', 
                    'gif', 'png', 'pdf', 'pptx',
                    'doc', 'txt', 'docx', 'ppt',
                    'xlsx', 'xlx'].includes(extension)){
            alert('Unsupported file upload format.');
            return;
        }
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
        let data = new FormData();
        data.append('attachment', file);
        data.append('message_text', file.name);
        data.append('chat',this.state.chatPk);
        data.append('sender',this.state.currentUser.id);
        
        axios.post('/messaging/api/bubble/', data).catch(error =>{
            console.log(error.response);
        })
    }

    render(){
        

        return(
            <Aux>
                <div className="row">
                    <div className="col-sm-12">
                        <ChatHeader 
                            title={this.state.receiver}
                            chatID={this.state.chatPk}
                            attachmentHandler={this.attachmentHandler}
                            />
                    </div>
                </div>
                <hr className="my-4" />
                <div className="row">
                <Aux>
                    <div className="col-sm-12 ">
                        <ChatWidget 
                            messages={this.state.messages}
                            owner={this.state.currentUser}
                            chat={this.state.chatPk}/>
                    </div>
                </Aux>
                </div>
            </Aux>    
        );
    }
}