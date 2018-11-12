import React, {Component} from 'react';
import ReplyWidget from './reply_widget';

class MessageDetail extends Component{
    state = {
        showReplyWidget: false,
        message: ""
    }

    toggleReply = () =>{
        this.setState((prevState) =>({
            showReplyWidget: !prevState.showReplyWidget
        }))
    }
    onSendReply = () =>{
        this.toggleReply();
        this.setState({message: "Reply sent sucessfully"})
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
                <button onClick={this.toggleReply}>
                    {this.state.showReplyWidget ? 'Cancel' : null} Reply
                </button>
                {this.state.showReplyWidget ? <ReplyWidget msgID={this.props.id}/> : null}
                {this.state.message}
        </div>
        )
    }
}

export default MessageDetail;