import React, {Component} from 'react';
import axios from 'axios';
import GroupChatWidget from '../components/chat/group';
import {Aux} from '../../src/common';
import ChatHeader from '../components/chat/chat_header';
import ReactModal from 'react-modal'
import AddParticipantsWidget from '../components/chat/add_participants';
export default class GroupChatRoot extends Component{
    constructor(props){
        super(props)
        const splitURL = window.location.href.split('/');
        const pk = splitURL[splitURL.length - 1];
        this.state = {
            messages: [],
            currentUser: null,
            groupPk: pk,
            selecting: false,
            selected: [],
            currentPage: 1,
            users: [],
            title: "",
            modalIsOpen: false,
            participantsModalOpen: false,
            participants: []
        }    
    }

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

      toggleContext = () => {
        //used to set up the context for selecting messages
        // to allow users to bulk select messages
        this.setState(
          prevState => ({ selecting: !prevState.selecting }),
          () => {
            if (!this.state.selecting) {
              this.setState({
                selected: [],
                title: this.state.name
              });
            }
          }
        );
      };

   
    componentDidMount(){

        this.intervalID = null;

        //get the message that provides its thread
        axios({
            'method': 'GET',
            'url': '/base/api/current-user'
        }).then(res => {
            this.setState({currentUser: {
                name: res.data.name,
                id: res.data.pk
            },
        })
        })
        axios({
            method: "GET",
            url: "/base/api/users"
          }).then(res => {
            this.setState({
              users: res.data
            });
          });
        this.getMessages()
        this.intervalID = setInterval(this.getLatest, 1000);
    }


    getMessages =() =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/group/' + this.state.groupPk
        }).then( res => {
            this.setState({
                messages: res.data.messages,
                name: res.data.name,
                participants: res.data.participants,
                title: this.state.selecting 
                        ? "(" + this.state.selected.length + ") selected" 
                        : res.data.name 
            })
            ;
        })
    }

    scrollToBottom = () =>{
        const chatBody = document.getElementById('chat-body');
        chatBody.scrollTop = chatBody.scrollHeight;
      }

    getLatest = () =>{
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

        const latest = Math.max(...this.state.messages.map(msg => (msg.id)));
        axios({
            url: '/messaging/api/group/get-latest/' +this.state.groupPk,
            method: 'POST',
            data: {
                latest: latest
            }
        }).then(res =>{
            if(res.data.messages.length === 0){
                return null;
            }
            this.setState(prevState => ({
                messages: prevState.messages.concat(res.data.messages)
            }), this.scrollToBottom)
        }).catch(error =>{
            console.log(error)
        })
    }

    loadMoreMessages = () =>{
        console.log('loading')
        this.setState(prevState => ({currentPage: prevState.currentPage + 1}), 
            () =>{
                console.log(this.state.currentPage)
                axios.get('/messaging/api/group/'+ this.state.groupPk +'/',
                        {
                            params: {
                                page: this.state.currentPage
                            }
                        }
                    ).then(res =>{
                        console.log(res.data)
                        this.setState(prevState =>{
                            return {
                                messages: res.data.messages.reverse()
                                    .concat(prevState.messages)}
                        })
                    }).catch(() =>{
                        alert('No more older messages')
                    })
        })
    }

    attachmentHandler = (evt) =>{
        const file = evt.target.files[0];
        const extension = file.name.split('.')[1];

        if(file.size > 5000000){
            alert('Cannot Upload files larger than 5MB');
            return;
        }else if(!['jpg', 'jpeg', 
                    'gif', 'png', 'pdf', 'pptx',
                    'doc', 'txt', 'docx', 'ppt',
                    'xlsx', 'xlx'].includes(extension)){
            alert('Unsupported file upload format.');
            return;
        }
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
        let data = new FormData();
        data.append('attachment', file);
        data.append('message_text', file.name);
        data.append('group',this.state.groupPk);
        data.append('sender',this.state.currentUser.id);
        
        axios.post('/messaging/api/bubble/', data).catch(error =>{
            console.log(error.response);
        })
    }

    toggleParticipantsModal = () =>{
        this.setState({participantsModalOpen: true})
    }

    addParticipant = (id) =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/add-group-participant/' + this.state.groupPk
                + '/' + id,
            
        }).then(res =>{
            this.setState({
                participants: res.data,
                participantsModalOpen: false
            })
        }).error(err =>{
            alert('An error occurred');
            this.setState({participantsModalOpen: false})
        })
    }

    removeParticipant = (id) =>{
        axios({
            'method': 'GET',
            'url': '/messaging/api/remove-group-participant/' + this.state.groupPk
                + '/' + id,
            
        }).then(res =>{
            this.setState({
                participants: res.data,
                participantsModalOpen: false
            })
        }).error(err =>{
            alert('An error occurred');
            this.setState({participantsModalOpen: false})
        })
    }

    render(){
        return(
            <Aux>
                <div className="row">
                    <div className="col-sm-12">
                        <ChatHeader
                            toggleParticipants={this.toggleParticipantsModal}
                            deleteHandler={this.messageDeleteHandler}
                            toggleUsersModal={this.toggleUsersModal}
                            toggleContext={this.toggleContext}
                            selecting={this.state.selecting}
                            chatID={this.state.groupPk}
                            isGroup 
                            title={this.state.title}
                            attachmentHandler={this.attachmentHandler} />

                    </div>
                </div>
                <hr className="my-4" />
                <div className="row">
                <Aux>
                    <div className="col-sm-12 ">
                        <GroupChatWidget 
                            selectedMessages={this.state.selected}
                            selectingContext={this.state.selecting}
                            messageSelectHandler={this.messageSelectHandler}
                            messages={this.state.messages}
                            client={this.state.currentUser}
                            group={this.state.groupPk}/>
                    </div>
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
                    <AddParticipantsWidget 
                        closeModal={() =>this.setState({
                            participantsModalOpen: false
                        })}
                        addParticipant={this.addParticipant}
                        removeParticipant={this.removeParticipant}
                        participants={this.state.participants}
                        open={this.state.participantsModalOpen} />
                </Aux>
                </div>
            </Aux>    
        );
    }
}