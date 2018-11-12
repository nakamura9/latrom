import React, {Component} from 'react';
import ReplyWidget from './reply_widget';
import axios from 'axios';
import $ from 'jquery';

class MessageDetail extends Component{
    state = {
        showReplyWidget: false,
        message: "",
        reply: ""
    }

    toggleReply = () =>{
        this.setState((prevState) =>({
            showReplyWidget: !prevState.showReplyWidget
        }))
    }
        

    submitHandler = () =>{
        const token = $("input[name='csrfmiddlewaretoken']").val();
        let payload = new FormData();
        payload.set('reply', this.state.reply);
        payload.set('csrfmiddlewaretoken', token);
        axios({
            method: "POST",
            url: `/messaging/reply-message/${this.props.id}`,
            data: payload
                }).then(() => {
                    this.toggleReply();
                    this.setState({
                        message: "Reply sent sucessfully",
                        reply: ""
                    })

                })
    }
    textInputHandler = (evt) =>{
        this.setState({reply: evt.target.value});
    }

    render(){
        return(
            <div>
                <div className="card text-white bg-primary">
                    <div className="card-body">
                        <h4 className="card-title">Message Details</h4>
                        <p className="card-text" >Created: {this.props.created_timestamp}</p>
                        <p className="card-text">To: {this.props.recipient}</p>
                        {/*<p className="card-text">Copy: {this.props.copy.map((name) =>
                            (`${name};`)
                        )}</p>*/}    
                    </div>
                </div>
                <hr />
                <h6>Subject: {this.props.subject}</h6>
                <hr />
                <h6>Message Body:</h6>
                <p >
                    {this.props.body}
                </p>
                <hr />
                <button 
                    className="btn btn-primary"
                    onClick={this.toggleReply}>
                    
                    {this.state.showReplyWidget ? <span><i className="fas fa-times"></i>Cancel Reply</span> : <span><i className="fas fa-reply"></i> Reply</span>} 
                </button>
                <hr />
                {this.state.showReplyWidget 
                    ? <ReplyWidget 
                        clickHandler={this.submitHandler}
                        inputHandler={this.textInputHandler}
                        value={this.state.reply}    
                        msgID={this.props.id}/> 
                    : null}
                {this.state.message}
        </div>
        )
    }
}

export default MessageDetail;