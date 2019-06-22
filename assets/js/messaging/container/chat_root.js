import React, { Component } from "react";
import axios from "axios";
import ChatWidget from "../components/chat/chat";
import { Aux } from "../../src/common";
import ChatHeader from "../components/chat/chat_header";

import ReactModal from "react-modal";

export default class ChatRoot extends Component {
  constructor(props) {
    super(props);
    const splitURL = window.location.href.split("/");
    const pk = splitURL[splitURL.length - 1];
    this.state = {
      messages: [],
      currentPage: 1,
      currentUser: null,
      chatPk: pk,
      selecting: false,
      selected: [],
      users: [],
      title: "",
      modalIsOpen: false
    };
  }

  toggleContext = () => {
    //used to set up the context for selecting messages
    // to allow users to bulk select messages
    this.setState(
      prevState => ({ selecting: !prevState.selecting }),
      () => {
        if (!this.state.selecting) {
          this.setState({
            selected: [],
            title: this.state.receiver
          });
        }
      }
    );
  };

  componentDidMount() {
    this.intervalID = null;

    //set up the app with the current user
    axios({
      method: "GET",
      url: "/base/api/current-user"
    }).then(res => {
      this.setState({
        currentUser: {
          name: res.data.name,
          id: res.data.pk
        }
      });
    });
    axios({
        method: "GET",
        url: "/base/api/users"
      }).then(res => {
        this.setState({
          users: res.data
        });
      });
    this.getMessages();
    this.intervalID = setInterval(this.getLatest, 1000);
  }

  scrollToBottom = () => {
    //scrolls the chat widget to the bottom
    const chatBody = document.getElementById("chat-body");
    chatBody.scrollTop = chatBody.scrollHeight;
  };

  getLatest = () => {
    //retrieves the unrendered messages from the server by comparing the
    //latest message id in the window with that stored in the server
    const latest = Math.max(...this.state.messages.map(msg => msg.id));
    axios({
      url: "/messaging/api/chat/get-latest/" + this.state.chatPk,
      method: "POST",
      data: {
        latest: latest
      }
    })
      .then(res => {
        if (res.data.messages.length === 0) {
          return null;
        }
        this.setState(
          prevState => ({
            messages: prevState.messages.concat(res.data.messages)
          }),
          this.scrollToBottom
        );
      })
      .catch(error => {
        console.log(error);
      });
  };
  getMessages = () => {
    //get messages at component did mount
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

    axios({
      method: "GET",
      url: "/messaging/api/chat/" + this.state.chatPk
    }).then(res => {
      this.setState({
        messages: res.data.messages.reverse(),
        receiver: res.data.receiver,
        title: res.data.receiver
      });
    });
  };

  attachmentHandler = evt => {
    //ensures that a valid attachment file is provided
    //limitations on file sizes and types are enforced
    const file = evt.target.files[0];
    const extension = file.name.split(".")[1];

    if (file.size > 5000000) {
      alert("Cannot Upload files larger than 5MB");
      return;
    } else if (
      ![
        "jpg",
        "jpeg",
        "gif",
        "png",
        "pdf",
        "pptx",
        "doc",
        "txt",
        "docx",
        "ppt",
        "xlsx",
        "xlx"
      ].includes(extension)
    ) {
      alert("Unsupported file upload format.");
      return;
    }
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    let data = new FormData();
    data.append("attachment", file);
    data.append("message_text", file.name);
    data.append("chat", this.state.chatPk);
    data.append("sender", this.state.currentUser.id);

    axios.post("/messaging/api/bubble/", data).catch(error => {
      console.log(error.response);
    });
  };

  loadMoreMessages = () => {
    //called when a button is clicked to retrieve more messages for really long threads.
    this.setState(
      prevState => ({ currentPage: prevState.currentPage + 1 }),
      () => {
        axios
          .get("/messaging/api/chat/" + this.state.chatPk + "/", {
            params: {
              page: this.state.currentPage
            }
          })
          .then(res => {
            this.setState(prevState => {
              return {
                messages: res.data.messages.reverse().concat(prevState.messages)
              };
            });
          })
          .catch(() => {
            alert("No more older messages");
          });
      }
    );
  };

  messageSelectHandler = id => {
    // adds or removes clicked messages based on whether they have already been selected.
    let newlySelected = [...this.state.selected];
    if (this.state.selected.includes(id)) {
      newlySelected = newlySelected.filter(index => index != id);
    } else {
      newlySelected.push(id);
    }
    this.setState({
      selected: newlySelected,
      title: "(" + newlySelected.length + ") messages selected."
    });
  };
  toggleUsersModal = () => {
      //hides reveals the user modal
    this.setState(prevState => ({ modalIsOpen: !prevState.modalIsOpen }));
  };

  messageForwarding = (id) => {
      //called after the user is selected from the modal
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    
    axios.post('/messaging/api/forward-messages/' + id,
    {
        message_ids : this.state.selected
    }).then(res =>{
        window.location.href = res.data.redirect
    })
  };

  messageDeleteHandler = () => {
    //used to delete selected messages, both in the list and on the server
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

    axios
      .post("/messaging/api/delete-messages/", {
        message_ids: this.state.selected
      })
      .then(() => {
        let newMessages = this.state.messages.filter(
          msg => !this.state.selected.includes(msg.id)
        );
        this.setState({ messages: newMessages });
      });
  };

  render() {
    return (
      <Aux>
        <div className="row">
          <div className="col-sm-12">
            <ChatHeader
              deleteHandler={this.messageDeleteHandler}
              toggleUsersModal={this.toggleUsersModal}
              toggleContext={this.toggleContext}
              selecting={this.state.selecting}
              title={this.state.title}
              chatID={this.state.chatPk}
              attachmentHandler={this.attachmentHandler}
            />
            <ChatWidget
              selectedMessages={this.state.selected}
              selectingContext={this.state.selecting}
              messages={this.state.messages}
              owner={this.state.currentUser}
              messageSelectHandler={this.messageSelectHandler}
              chat={this.state.chatPk}
              loadMoreMessages={this.loadMoreMessages}
            />
            <ReactModal
                isOpen={this.state.modalIsOpen}
                parentSelector={() => document.getElementById('chat-body')}>
              <h4>Select a user to forward to.</h4>
              <ul className="list-group">
                {this.state.users.map(user => (
                  <li
                    className="list-group-item"
                    onClick={() => this.messageForwarding(user.id)}
                  >
                    {user.username}
                  </li>
                ))}
              </ul>
              <button 
              className="btn btn-danger"
              onClick={() => this.setState({modalIsOpen: false})}> <i className="fas fa-times"></i> Cancel</button>
            </ReactModal>
          </div>
        </div>
      </Aux>
    );
  }
}
