import React, {Component} from 'react';
import axios from 'axios';
import $ from 'jquery';

class SMSMessageThreadView extends Component{
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
        const token = $("input[name='csrfmiddlewaretoken']").val();
        let payload = new FormData();
        payload.set('reply', this.state.inputText);
        payload.set('csrfmiddlewaretoken', token)
        
        axios({
            'method': 'POST',
            'url': `/messaging/reply-message/${this.props.msgID}`,
            'data': payload
        });
        this.setState({inputText: ""});
    }

    
    render(){
        return(
            <div>
                <div style={{
                    "maxHeight": "500px",
                    "overflowY": "auto"
                }}>
                    {this.state.messages.map((message) =>(
                        <MessageBubble 
                            isSender={message.sender === this.props.owner}
                            body={message.body}
                            created={message.created_timestamp}
                        />
                    ))}
                </div>
                <div>
                    <textarea 
                        cols={3} 
                        style={{
                            borderRadius: "10px",
                            border: "1px solid #09f",
                            width: "85%"
                        }} 
                        value={this.state.inputText}
                        onChange={this.inputHandler}/>
                        <button 
                            style={{
                                color: "white",
                                backgroundColor: "#55f",
                                border:"0px",
                                borderRadius: "20px",
                                padding: '10px'
                            }}
                            onClick={this.sendMessage}>Send</button>
                </div>
            </div>
        )
    }
}

class MessageBubble extends Component{
    render(){
        return(
            <div style={{
                backgroundColor: this.props.isSender ? "#05f" : "#0cf",
                color: "white",
                borderRadius: "10px",
                padding: "10px",
                margin: "10px",
                width: '85%',
                float: this.props.isSender ? 'left' : 'right'
            }}>
                <p>{this.props.body}<br /><span style={{
                    float: "right",
                    color: "#ddd"
                }}>{this.props.created}</span></p>
                
            </div>
        )
    }
}

export default SMSMessageThreadView;