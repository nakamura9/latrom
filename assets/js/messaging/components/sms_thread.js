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
            <div style={{
                
                "maxWidth" : "600px",
                "margin" : "0px auto",
            }}>
                <div style={{
                    "overflowY": "auto",
                    "minHeight": "400px",
                    "height": "400px"
                }}>
                    {this.state.messages.map((message, i) =>(
                        <MessageBubble
                            MessageID={i} 
                            isSender={message.sender === this.props.owner}
                            body={message.body}
                            created={message.created_timestamp}
                        />
                    ))}
                </div>
                <div>
                    <div className="input-group">
                        <textarea 
                            className="form-control"
                            cols={3} 
                            style={{
                                borderRadius: "10px",
                                border: "1px solid #09f",
                                width: "80%"
                            }} 
                            value={this.state.inputText}
                            onChange={this.inputHandler}/>
                    <div className="input-group-append">
                        <button 
                            style={{
                                color: "white",
                                backgroundColor: "#07f",
                                border:"0px",
                                height: '64px',
                                borderRadius: "20px"
                            }}
                            onClick={this.sendMessage}> <b style={{
                                fontSize: "16pt"
                            }}>Send</b> <i className="fas fa-angle-double-right"></i></button>
                    </div>
                    </div>
                </div>
            </div>
        )
    }
}

const {
        return(
            <div style={{
                backgroundColor: props.isSender ? "#05f" : "#0cf",
                color: "white",
                borderRadius: "10px",
                padding: "10px",
                margin: "10px",
                width: '85%',
                float: props.isSender ? 'left' : 'right'
            }} id={`${props.MessageID}`}>
                <p>{props.body}<br /><span style={{
                    float: "right",
                    color: "#ddd"
                }}>{props.created}</span></p>
                
            </div>
        )
    }
}

export default SMSMessageThreadView;