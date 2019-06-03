import React, {Component} from 'react';
import axios from 'axios';
import MessageBubble from './bubble';
import ChatInput from './chat_input';

class groupChatWidget extends Component{
    state = {
        messages: [],
        inputText: ""
    }

    componentDidUpdate = (prevProps, prevState) => {
        if(prevState.messages.length !== this.props.messages.length){
            this.setState({messages: this.props.messages});
        }
      }

    inputHandler = (evt) =>{
        this.setState({inputText: evt.target.value});
    }

    sendMessage = () =>{
       
       axios.defaults.xsrfCookieName = 'csrftoken'
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
    
        const data = {
            'message_text': this.state.inputText,
            'group': this.props.group,
            'sender': this.props.client.id
        }


        axios.post(`/messaging/api/bubble/`, data).catch((error)=> console.log(error.response));
        this.setState({inputText: ""});
    }

    
    render(){
        return(
            <div style={{
                
                "maxWidth" :  window.screen.width > 720 ? "50vw" : "98vw",
                "margin" : "0px auto",
            }} className="shadow">
                <div style={{
                    "overflowY": "auto",
                    "minHeight": "400px",
                    "height": "400px"
                }}>
                    {this.state.messages.map((message, i) =>(
                        <MessageBubble
                            showSender
                            key={i}
                            MessageID={i} 
                            isSender={message.sender.id === this.props.client.id}
                            message={message}
                            created={message.created_timestamp}
                        />
                    ))}
                </div>
                <ChatInput 
                    inputText={this.state.inputText}
                    inputHandler={this.inputHandler}
                    sendMessage={this.sendMessage}/>
            </div>
        )
    }
}

export default groupChatWidget;