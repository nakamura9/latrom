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
        $("#to").text(msg.recipient);
        $('#created').text(msg.created_timestamp);
        $('#subject').text(msg.subject);
        $("#message-body").text(msg.body);
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

    componentDidMount(){
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];
        //get the message that provides its thread

        axios({
            'method': 'GET',
            'url': '/messaging/api/message/'+ pk,
        }).then(res => {
            axios({
                'method': 'GET',
                'url': '/messaging/api/message-thread/' + res.data.thread_pk
            }).then( res => {
                this.setState({messages: res.data.messages.map((message, i) =>(res.data.messages[res.data.messages.length - i - 1]))    
            });
            
        })
    });
}
    
    render(){
        
        return(
            <div>
                <h4>Message Thread</h4>
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
        )
    }
}

const MessageCard = (props) =>{
    let messageStyle = {
        border: "1px solid black",
        padding: "10px"
    }
    if(props.unread){
        messageStyle.backgroundColor = '#08f';
        messageStyle.color = 'white';
    }
    if(props.focused){
        messageStyle.border = "3px solid #04f";
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