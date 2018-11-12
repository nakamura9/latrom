import React, {Component} from 'react';
import axios from 'axios';
import $ from 'jquery';

//completely broken will work on it later


class ThreadWidget extends Component{
    state = {
        messages: [],
        focused: null
    }


    messageClickHandler = (index) => {
    
        //set the message content to 
        let msg = this.state.messages[index];
        this.setState({focused: index});
        this.markAsRead(index);
        this.props.setCurrent(msg);

    }

    componentDidUpdate = (prevProps, prevState) => {
      if(prevState.messages.length !== this.props.messages.length){
            let messages = [...this.props.messages].reverse();
            this.setState({messages: messages});
            
      }
    }
    

    markAsRead = (index) => {
        const pk = this.state.messages[index].id;
        axios({
            method: 'GET',
            url: '/messaging/api/mark-as-read/' + pk
    }).then(res => {
        let msg = {...this.state.messages[index]};
        msg['read'] = true;
        let newMessages = [...this.state.messages];
        newMessages[index] = msg;
        this.setState({messages: newMessages});
    });
    }
    render(){
        return(
            <div>
                <h4>Message Thread</h4>
                <div style={{
                    overflowY: 'auto',
                    height: '500px'
                }}>
                    {this.state.messages.length === 0 ? 'No messages To display' : null}
                    {this.state.messages.map((message, i) =>(
                        <MessageCard 
                            key={i}
                            messageID={i}
                            focused={this.state.focused === i}
                            unread={!message.read}
                            subject={message.subject}
                            timestamp={message.created_timestamp}
                            sender={message.sender}
                            clickHandler={this.messageClickHandler}

                        />
                    ))}
                </div>
                
            </div>
        )
    }
}

const MessageCard = (props) =>{
    let messageStyle = {
        borderTop: "1px solid white",
        padding: "10px",
        backgroundColor: '#09f',
        color: 'white'
    }
    if(props.unread){
        messageStyle.backgroundColor = '#08f';
        messageStyle.color = 'white';
    }
    if(props.focused){
        messageStyle.backgroundColor = "#007bff";
    }
    return(
        <div 
            style={messageStyle}
            onClick={() => props.clickHandler(props.messageID)}>
            <h5>
                {props.timestamp}
            </h5>
            <hr />
            <h6>{props.sender}</h6>
            <p>{props.subject}</p>        
        </div>
    )
}

export default ThreadWidget;