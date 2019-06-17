import React, { Component } from "react";
import ReplyWidget from "./reply_widget";
import axios from "axios";
import { Aux } from "../../../src/common";
import ReactModal from "react-modal";
import SearchableWidget from "../../../src/components/searchable_widget";
import MultipleSelectWidget from "../../../src/multiple_select/containers/root";

class MessageDetail extends Component {
  state = {
    showReplyWidget: false,
    message: "",
    attachment: null,
    subject: "",
    created_timestamp: "",
    reply: "",
    replyStatus: "open",
    forwardModalIsOpen: false,
    forwardTo: "",
    forwardCopy: [],
    forwardBlindCopy: []
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
    this.setState({ replyStatus: "sending" });
    axios
      .get("/messaging/api/send-draft/" + this.state.id + "/")
      .then(res => {
        if (res.data.status === "ok") {
          this.setState({ replyStatus: "sent" });
        }
      })
      .catch(() => {
        this.setState({ replyStatus: "error" });
      });
  };

  submitHandler = () => {
    this.setState({ replyStatus: "sending" });
    let data = new FormData();
    data.append("attachment", this.state.attachment);
    data.append("body", JSON.stringify(this.state.reply));

    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

    axios
      .post(`/messaging/api/reply-email/${this.state.id}/`, data)
      .then(res => {
        if (res.data.status === "ok") {
          this.setState({ replyStatus: "sent" });
        } else {
          this.setState({ replyStatus: "error" });
        }
      })
      .catch(() => {
        this.setState({ replyStatus: "error" });
      });
  };

  setReply = data => {
    this.setState({ reply: data });
  };

  attachmentHandler = file => {
    this.setState({ attachment: file });
  };

  setForwardCopy = data => {
    this.setState({ forwardCopy: data });
  };

  setForwardBlindCopy = data => {
    this.setState({ forwardBlindCopy: data });
  };

  forwardMessage = () => {
    axios
      .post("/messaging/api/forward-email/" + this.props.messageID, {
        to: this.state.forwardTo,
        copy: this.state.forwardCopy,
        blind_copy: this.state.forwardBlindCopy
      })
      .then(res => {
        this.setState({ forwardModalIsOpen: false });
      });
  };

  render() {
    let replyView = null;
    if (
      this.state.replyStatus === "open" &&
      ["inbox", "drafts"].includes(this.state.folder)
    ) {
      replyView = (
        <div>
          <input type="hidden" name="copy" id="id_copy" />
          <input type="hidden" name="blind_copy" id="id_blind_copy" />
          <div className="btn-group">
            <button
              className="btn btn-primary"
              onClick={() => this.setState({ forwardModalIsOpen: true })}
            >
              <i className="fa fa-arrow-right" /> Forward Message
            </button>
            {this.state.attachment ? (
              <a href={this.state.attachment} className="btn btn-info" download>
                Download Attachment
              </a>
            ) : null}
            {this.props.draft ? (
              <Aux>
                <button className="btn btn-primary" onClick={this.sendDraft}>
                  <i class="fas fa-envelope-open" /> Send
                </button>
                <a
                  className="btn btn-primary"
                  href={"/messaging/email/update-draft/" + this.props.messageID}
                >
                  <i class="fas fa-edit" /> Edit Draft
                </a>
              </Aux>
            ) : (
              <button className="btn btn-primary" onClick={this.toggleReply}>
                {this.state.showReplyWidget ? (
                  <span>
                    <i className="fas fa-times" />
                    Cancel Reply
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
              attachmentHandler={this.attachmentHandler}
              clickHandler={this.submitHandler}
              setReply={this.setReply}
              value={this.state.reply}
              msgID={this.props.id}
            />
          ) : null}
        </div>
      );
    } else if (this.state.replyStatus === "sent") {
      replyView = <h3>Email Sent</h3>;
    } else if (this.state.replyStatus === "sending") {
      replyView = (
        <img
          width="150"
          height="150"
          src="/static/common_data/images/spinner.gif"
          alt=""
        />
      );
    } else if (this.state.folder !== "inbox") {
      replyView = (
        <div className="btn-group">
          <button
            className="btn btn-primary"
            onClick={() => this.setState({ forwardModalIsOpen: true })}
          >
            <i className="fa fa-arrow-right" /> Forward Message
          </button>
          {this.state.attachment ? (
            <a href={this.state.attachment} className="btn btn-info" download>
              Download Attachment
            </a>
          ) : null}
        </div>
      );
    } else {
      replyView = (
        <div>
          <h3>Email Send Error</h3>;
          <button
            className="btn btn-primary"
            onClick={() => this.setState({ replyStatus: "open" })}
          >
            Retry
          </button>
        </div>
      );
    }

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

        
        {replyView}
        <ReactModal
          isOpen={this.state.forwardModalIsOpen}
          parentSelector={() => document.body}
        >
          <h4>Forward Message</h4>

          <div>
            <p>To:</p>
            <SearchableWidget
              onSelect={value => {
                this.setState({ forwardTo: value });
              }}
              onClear={() => {
                this.setState({ forwardTo: "" });
              }}
              newLink="/messaging/create-email-address"
              dataURL="/messaging/api/email-address"
              displayField="address"
              idField="id"
            />
            <p>Cc:</p>
            <MultipleSelectWidget
              resProcessor={res => res.data.copy}
              inputField="copy"
              dataURL="/messaging/api/email-address"
              nameField="address"
              selectHook={this.setForwardCopy}
            />
            <p>Bcc:</p>
            <MultipleSelectWidget
              resProcessor={res => res.data.copy}
              inputField="blind_copy"
              dataURL="/messaging/api/email-address"
              nameField="address"
              selectHook={this.setForwardBlindCopy}
            />
            <div className="btn-group">
              <button className="btn btn-primary" onClick={this.forwardMessage}>
                Send
              </button>
              <button
                className="btn btn-danger"
                onClick={() => {
                  this.setState({
                    forwardTo: "",
                    forwardBlindCopy: [],
                    forwardCopy: [],
                    forwardModalIsOpen: false
                  });
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </ReactModal>
        <p>{this.state.text}</p>
        <div dangerouslySetInnerHTML={{ __html: this.state.body }} />
        </div>
    );
  }
}

export default MessageDetail;
