import React, {Component} from 'react';
import ReplyWidget from './reply_widget';
import axios from 'axios';

class MessageDetail extends Component{
    state = {
        showReplyWidget: false,
        message: "",
        subject: "",
        recipient: "",
        created_timestamp: "",
        reply: ""
    }

    toggleReply = () =>{
        this.setState((prevState) =>({
            showReplyWidget: !prevState.showReplyWidget
        }))
    }

    componentDidUpdate(prevProps, prevState) {
        if(this.props.messageID !== prevProps.messageID){
            axios.get('/messaging/api/email/' + this.props.messageID).then(res =>{
                this.setState({
                    'message': res.data.body,
                    'subject': res.data.subject,
                    'recipient': res.data.to,
                    'sender': res.data.sender,
                    'created_timestamp': res.data.created_timestamp
                })
            })
        }
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
        if(!this.props.messageID){
            return(
                <div>
                    <h3 style={{textAlign: "center"}}>View selected Messages here.</h3>
                    <div style={{
                        margin: "0px auto",
                        width: "20rem"
                    }}>
                        <i className="fas fa-envelope" style={{
                            fontSize: "20rem",
                            color: "#aaa"
                        }}></i>
                    </div>
                </div>
            )
        }
        return(
            <div >
                <div className="card text-white bg-primary">
                    <div className="card-body">
                        <h4 className="card-title">{this.state.subject}</h4>
                        <p className="card-text" >From: {this.state.sender}</p>
                        <p className="card-text">To: {this.state.recipient}</p>
                        <p className="card-text">Created: {this.state.created_timestamp}</p>
                    </div>
                </div>
                <hr />
                <h6>Message Body:</h6>
                <p >
                    {this.state.message}
                </p>
                <hr />
                <div>
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
                </div>
                
        </div>
        )
    }
}

export default MessageDetail;