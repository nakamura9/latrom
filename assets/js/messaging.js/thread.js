import React, {Component} from 'react';
import axios from 'axios';
import $ from 'jquery';

//completely broken will work on it later


class ThreadWidget extends Component{
    state = {
        messages = []
    }
    messageClickHandler = (id) => {
            
    }

    componentDidMount(){

        const pk = $('#id_thread_pk').val();

        axios({
            'method': 'GET',
            'url': '/messaging/api/thread-list/'+ pk,
        }).then(res = >{
            this.setState({messages: res.data});
        })
    }
    
    render(){
        
        return(
            <div>
                {this.state.messages.map((message, i) =>(
                    <MessageCard 
                        key={i}
                        messageID={i}
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
            <h6>{props.title}
                <span style={{float: 'right'}}>{props.timestamp}</span>
            </h6>
            <hr />
            <p>{props.contentPreview}</p>        
        </div>
    )
}