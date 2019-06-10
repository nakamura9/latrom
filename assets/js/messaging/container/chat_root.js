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
            currentPage: 1,
            currentUser: null,
            chatPk: pk,
            selecting: false,
            selected: []
        }    
    }
    
    toggleContext = () =>{
        console.log('context')
        this.setState(prevState => ({selecting: !prevState.selecting}));
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
        this.getMessages()
        this.intervalID = setInterval(this.getLatest, 1000);

    }

    scrollToBottom = () =>{
        const chatBody = document.getElementById('chat-body');
        chatBody.scrollTop = chatBody.scrollHeight;
      }

    getLatest = () =>{
        console.log('setting up')

        const latest = Math.max(...this.state.messages.map(msg => (msg.id)));
        axios({
            url: '/messaging/api/chat/get-latest/' +this.state.chatPk,
            method: 'POST',
            data: {
                latest: latest
            }
        }).then(res =>{
            if(res.data.messages.length === 0){
                return null;
            }
            this.setState(prevState => ({
                messages: prevState.messages.concat(res.data.messages)
            }), this.scrollToBottom)
        }).catch(error =>{
            console.log(error)
        })
    }
    getMessages =() =>{
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

        axios({
            'method': 'GET',
            'url': '/messaging/api/chat/' + this.state.chatPk
        }).then( res => {
            this.setState({
                messages: res.data.messages.reverse(),
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

    loadMoreMessages = () =>{
        console.log('loading')
        this.setState(prevState => ({currentPage: prevState.currentPage + 1}), 
            () =>{
                console.log(this.state.currentPage)
                axios.get('/messaging/api/chat/'+ this.state.chatPk +'/',
                        {
                            params: {
                                page: this.state.currentPage
                            }
                        }
                    ).then(res =>{
                        console.log(res.data)
                        this.setState(prevState =>{
                            return {
                                messages: res.data.messages.reverse()
                                    .concat(prevState.messages)}
                        })
                    }).catch(() =>{
                        alert('No more older messages')
                    })
        })
    }

    render(){
        

        return(
            <Aux>
                <div className="row">
                    <div className="col-sm-12">
                        <ChatHeader 
                            toggleContext={this.toggleContext}
                            selecting={this.state.selecting}
                            title={this.state.receiver}
                            chatID={this.state.chatPk}
                            attachmentHandler={this.attachmentHandler}
                            />
                        <ChatWidget 
                            messages={this.state.messages}
                            owner={this.state.currentUser}
                            chat={this.state.chatPk}
                            loadMoreMessages={this.loadMoreMessages}/>
                    </div>
                </div>
            </Aux>
        );
    }
}