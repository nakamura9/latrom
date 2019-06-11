import React, { Component } from "react";
import axios from "axios";
import MessageBubble from "./bubble";
import ChatInput from "./chat_input";
import styles from "./chatStyles.css";

class ChatWidget extends Component {
  state = {
    inputText: "",
  };

  

  inputHandler = evt => {
    this.setState({ inputText: evt.target.value });
  };

  sendMessage = () => {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    const data = {
      message_text: this.state.inputText,
      chat: this.props.chat,
      sender: this.props.owner.id.toString()
    };

    axios
      .post(`/messaging/api/bubble/`, data)
      .then(() =>{
        this.setState({ inputText: "" });
        this.scrollToBottom()    
      })
      .catch(error => console.log(error.response));
  };


  render() {
    return (
      <div
        className={styles.messageContainer}
        style={{
          maxWidth: window.screen.width > 720 ? "50vw" : "98vw",
          margin: "0px auto",
          padding: "5px"
        }}
        className="shadow"
      >
        <div 
            id='chat-body'
          style={{
            overflowY: "auto",
            minHeight: "400px",
            height: "400px"
          }}
        >
          <div style={{width: "100%"}}>
                <div style={{
                    width: "25%",
                    margin: "5px auto"
                }}>
                    <button 
                        className="btn btn-primary" 
                        onClick={this.props.loadMoreMessages}>Load More</button>
                </div>
          </div>
          {this.props.messages.map((message, i) => {
            return (
              <MessageBubble
                selectedMessages={this.props.selectedMessages}
                selectHandler={this.props.messageSelectHandler}
                canBeSelected={this.props.selectingContext}
                key={i}
                latest={this.props.messages.length -1 === i}
                MessageID={i}
                isSender={message.sender.id === this.props.owner.id}
                message={message}
                created={message.created_timestamp}
              />
            );
          })}
        </div>
        <ChatInput
          inputText={this.state.inputText}
          inputHandler={this.inputHandler}
          sendMessage={this.sendMessage}
        />
      </div>
    );
  }
}

export default ChatWidget;
