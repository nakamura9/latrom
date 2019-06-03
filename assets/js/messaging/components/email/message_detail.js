import React, { Component } from "react";
import ReplyWidget from "./reply_widget";
import axios from "axios";

class MessageDetail extends Component {
  state = {
    showReplyWidget: false,
    message: "",
    subject: "",
    created_timestamp: "",
    reply: ""
  };

  toggleReply = () => {
    this.setState(prevState => ({
      showReplyWidget: !prevState.showReplyWidget
    }));
  };

  componentDidUpdate(prevProps, prevState) {
    if (this.props.messageID !== prevProps.messageID) {
      axios.get("/messaging/api/email/" + this.props.messageID).then(res => {
        this.setState({ ...res.data });
      });
    }
  }

  sendDraft = () => {
    axios.get("/messaging/api/send-draft/" + this.state.id + "/");
  };

  submitHandler = () => {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    axios({
      method: "POST",
      url: `/messaging/api/reply-email/${this.state.id}/`,
      data: {
        body: this.state.reply
      }
    });
  };

  setReply = data => {
    this.setState({ reply: data });
  };

  render() {
    if (!this.props.messageID) {
      return (
        <div>
          <h3 style={{ textAlign: "center" }}>View selected Messages here.</h3>
          <div
            style={{
              margin: "0px auto",
              width: "20rem"
            }}
          >
            <i
              className="fas fa-envelope"
              style={{
                fontSize: "20rem",
                color: "#aaa"
              }}
            />
          </div>
        </div>
      );
    }
    return (
      <div>
        <div className="card text-white bg-primary">
          <div className="card-body">
            <h4 className="card-title">{this.state.subject}</h4>
            <p className="card-text">From: {this.state.sent_from}</p>
            <p className="card-text">To: {this.state.to}</p>
            {this.state.copy && this.state.copy.length > 0 ? (
              <p className="card-text">Cc: {this.state.copy.join("; ")}</p>
            ) : null}
            {this.state.blind_copy && this.state.blind_copy.length > 0 ? (
              <p className="card-text">
                Bcc: {this.state.blind_copy.join("; ")}
              </p>
            ) : null}
            <p className="card-text">Created: {this.state.created_timestamp}</p>
          </div>
        </div>
        <hr className="my-4" />
        <div dangerouslySetInnerHTML={{ __html: this.state.body }} />
        <div>
          <div className="btn-group">
            {this.props.draft ? (
              <button 
                className="btn btn-primary"
                onClick={this.sendDraft}>
                <i class="fas fa-envelope-open" /> Send
              </button>
            ) : (
              <button className="btn btn-primary" onClick={this.toggleReply}>
                {this.state.showReplyWidget ? (
                  <span>
                    <i className="fas fa-times" />Cancel Reply
                  </span>
                ) : (
                  <span>
                    <i className="fas fa-reply" /> Reply
                  </span>
                )}
              </button>
            )}
          </div>

          <hr />
          {this.state.showReplyWidget ? (
            <ReplyWidget
              clickHandler={this.submitHandler}
              setReply={this.setReply}
              value={this.state.reply}
              msgID={this.props.id}
            />
          ) : null}
        </div>
      </div>
    );
  }
}

export default MessageDetail;