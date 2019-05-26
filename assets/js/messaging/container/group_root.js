import React, {Component} from 'react';
import axios from 'axios';
import GroupChatWidget from '../components/group';
import {Aux} from '../../src/common';
import ChatHeader from '../components/chat_header';

export default class GroupChatRoot extends Component{
    state = {
        messages: [],
        currentMessage: null,
        currentUser: null,
        isTextMessageView: false,
        groupPk: null,
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
                url: `/messaging/api/close-thread/${this.state.groupPk}`,
                method: "GET"
            })
        }   
    }

    getMessages =(thread) =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/group/' + thread
        }).then( res => {
            this.setState({
                messages: res.data.messages,
                currentMessage: res.data.messages[res.data.messages.length - 1],
                name: res.data.name
                
            });
        })
    }
    updateMessages = () =>{    
        if(this.state.groupPk === null){
            const splitURL = window.location.href.split('/');
            const pk = splitURL[splitURL.length - 1];
            axios({
                'method': 'GET',
                'url': '/messaging/api/group/'+ pk,
            }).then(res =>{
                this.setState({groupPk: pk}, 
                    () => this.getMessages(pk));
            })    
        }else{
            this.getMessages(this.state.groupPk);
        }
    }

    render(){
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];

        
        return(
            <Aux>
                <div className="row">
                    <div className="col-sm-12">
                        <ChatHeader title={this.state.name}/>
                    </div>
                </div>
                <hr className="my-4" />
                <div className="row">
                <Aux>
                    <div className="col-sm-12 ">
                        <GroupChatWidget 
                            messages={this.state.messages}
                            client={this.state.currentUser}
                            group={pk}/>
                    </div>
                </Aux>
                </div>
            </Aux>    
        );
    }
}