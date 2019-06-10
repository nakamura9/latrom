import React, {Component} from 'react';
import axios from 'axios';
import GroupChatWidget from '../components/chat/group';
import {Aux} from '../../src/common';
import ChatHeader from '../components/chat/chat_header';


export default class GroupChatRoot extends Component{
    constructor(props){
        super(props)
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];
        this.state = {
            messages: [],
            currentUser: null,
            groupPk: pk,
        }    
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


    getMessages =() =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/group/' + this.state.groupPk
        }).then( res => {
            console.log(res.data)
            this.setState({
                messages: res.data.messages,
                name: res.data.name
            });
        })
    }

    scrollToBottom = () =>{
        const chatBody = document.getElementById('chat-body');
        chatBody.scrollTop = chatBody.scrollHeight;
      }

    getLatest = () =>{
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

        const latest = Math.max(...this.state.messages.map(msg => (msg.id)));
        axios({
            url: '/messaging/api/group/get-latest/' +this.state.groupPk,
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

    loadMoreMessages = () =>{
        console.log('loading')
        this.setState(prevState => ({currentPage: prevState.currentPage + 1}), 
            () =>{
                console.log(this.state.currentPage)
                axios.get('/messaging/api/group/'+ this.state.groupPk +'/',
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