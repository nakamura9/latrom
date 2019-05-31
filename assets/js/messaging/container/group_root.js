import React, {Component} from 'react';
import axios from 'axios';
import GroupChatWidget from '../components/group';
import {Aux} from '../../src/common';
import ChatHeader from '../components/chat_header';

export default class GroupChatRoot extends Component{
    constructor(props){
        super(props)
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];
        this.state = {
            messages: [],
            currentMessage: null,
            currentUser: null,
            groupPk: pk,
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
            'url': '/messaging/api/group/' + this.state.groupPk
        }).then( res => {
            this.setState({
                messages: res.data.messages,
                currentMessage: res.data.messages[res.data.messages.length - 1],
                name: res.data.name
            });
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
        data.append('group',this.state.groupPk);
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
                            chatID={this.state.groupPk}
                            isGroup 
                            title={this.state.name}
                            attachmentHandler={this.attachmentHandler} />

                    </div>
                </div>
                <hr className="my-4" />
                <div className="row">
                <Aux>
                    <div className="col-sm-12 ">
                        <GroupChatWidget 
                            messages={this.state.messages}
                            client={this.state.currentUser}
                            group={this.state.groupPk}/>
                    </div>
                </Aux>
                </div>
            </Aux>    
        );
    }
}