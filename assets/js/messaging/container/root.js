import React, {Component} from 'react';
import Thread from '../components/thread';
import MessageDetail from '../components/message_detail';
import axios from 'axios';
import SMSMessageThreadView from '../components/sms_thread';
import {Aux} from '../../../js/src/common';

export default class MessageDetailView extends Component{
    state = {
        messages: [],
        currentMessage: null,
        currentUser: null,
        isTextMessageView: false,
        threadPK: null,
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
            this.setState({currentUser: res.data.name})
        })

        this.updateMessages()
    }

    toggleView = () => {
        this.setState((prevState) => ({
            isTextMessageView: !prevState.isTextMessageView
        }), () =>{
            if(this.state.isTextMessageView){
                this.intervalID = setInterval(this.updateMessages, 3000);
            }else{
                if(this.intervalID){
                    clearInterval(this.intervalID);
                }
            }
        });
    }

    getMessages =(thread_pk) =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/message-thread/' + thread_pk
        }).then( res => {
            this.setState({
                messages: res.data.messages,
                currentMessage: res.data.messages[res.data.messages.length - 1]    
            });
        })
    }
    updateMessages = () =>{    
        if(this.state.threadPK === null){
            const splitURL = window.location.href.split('/');
            const pk = splitURL[splitURL.length - 1];
            axios({
                'method': 'GET',
                'url': '/messaging/api/message/'+ pk,
            }).then(res =>{
                this.setState({threadPK: res.data.thread_pk}, 
                    () => this.getMessages(res.data.thread_pk));
            })    
        }else{
            this.getMessages(this.state.threadPK);
        }
    }

    render(){
        //need to find a better way
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];

        
        return(
            <Aux>
                <div className="row">
                    <div className="col-sm-12">
                        <button 
                            className={`btn btn-${this.state.isTextMessageView 
                                ? 'primary' 
                                : 'secondary'}`}
                            onClick={this.toggleView}>
                                {this.state.isTextMessageView 
                                    ? 'Email View' 
                                    : 'Text Messaging View'}</button>
                    </div>
                </div>
                <div className="row">
                <Aux>
                    <div
                        style={{
                            display: this.state.isTextMessageView 
                                ? "none" 
                                : "block"
                        }}
                        className="col-sm-4">
                        <Thread 
                            messages={this.state.messages}
                            setCurrent={this.setCurrentMessage}/>
                    </div>
                    <div 
                        style={{
                            display: this.state.isTextMessageView 
                                ? "none" 
                                : "block"
                        }}
                        className="col-sm-8">
                        <MessageDetail
                            {...this.state.currentMessage} />
                    </div>
                    <div 
                        style={{
                            display: this.state.isTextMessageView 
                                ? "block" 
                                : "none"
                        }}
                        className="col-sm-12">
                        <SMSMessageThreadView 
                            messages={this.state.messages}
                            owner={this.state.currentUser}
                            msgID={pk}/>
                    </div>
                </Aux>
                </div>
            </Aux>    
        );
    }
}