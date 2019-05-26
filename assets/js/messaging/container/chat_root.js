import React, {Component} from 'react';
import axios from 'axios';
import ChatWidget from '../components/chat';
import {Aux} from '../../src/common';
import ChatHeader from '../components/chat_header';

export default class ChatRoot extends Component{
    state = {
        messages: [],
        currentMessage: null,
        currentUser: null,
        isTextMessageView: false,
        chatPk: null,
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
        this.intervalID = setInterval(this.updateMessages, 3000);

        this.updateMessages()
    }

    closeThread = () =>{
        if(confirm('Are you sure you want to close this thread?')){
            axios({
                url: `/messaging/api/close-chat/${this.state.chatPk}`,
                method: "GET"
            })
        }   
    }

    getMessages =(thread) =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/chat/' + thread
        }).then( res => {
            this.setState({
                messages: res.data.messages,
                currentMessage: res.data.messages[res.data.messages.length - 1],
                receiver: res.data.receiver
            });
        })
    }
    updateMessages = () =>{    
        if(this.state.chatPk === null){
            const splitURL = window.location.href.split('/');
            const pk = splitURL[splitURL.length - 1];
            axios({
                'method': 'GET',
                'url': '/messaging/api/chat/'+ pk,
            }).then(res =>{
                this.setState({chatPk: pk}, 
                    () => this.getMessages(pk));
            })    
        }else{
            this.getMessages(this.state.chatPk);
        }
    }

    render(){
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];

        console.log(this.state.currentUser)
        return(
            <Aux>
                <div className="row">
                    <div className="col-sm-12">
                        <ChatHeader title={this.state.receiver}/>
                    </div>
                </div>
                <hr className="my-4" />
                <div className="row">
                <Aux>
                    <div className="col-sm-12 ">
                        <ChatWidget 
                            messages={this.state.messages}
                            owner={this.state.currentUser}
                            chat={pk}/>
                    </div>
                </Aux>
                </div>
            </Aux>    
        );
    }
}