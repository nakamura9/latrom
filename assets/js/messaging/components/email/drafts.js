import React from 'react';
import axios from 'axios';
import ListItem from './message_list_item';


class DraftList extends React.Component{
    state = {
        messages: [],
        currentPage: 1

    }
    componentDidMount(){
        axios.get('/messaging/api/drafts/').then(res =>{
            this.setState({messages: res.data})
        })
    }

    setCurrent = (id, index) =>{
        let newMessages = [...this.state.messages];
        let newMsg = newMessages[index];
        newMsg.read = true;
        newMessages[index] = newMsg;
        this.setState({messages: newMessages})
        this.props.setCurrent(id, true);
    }

    loadMoreMessages = () =>{
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
        
        axios.get('/messaging/api/drafts/', {
            params: {
                page: this.state.currentPage + 1
            }
    }).then( res =>{
            this.setState(prevState => ({
                currentPage: prevState.currentPage + 1,
                messages: res.data.concat(prevState.messages) 
            }))
        }).catch(error =>{
            alert('No more email messages')
        })
    }
    
    render(){
        return(
            <ul className="list-group">
                {this.state.messages.length === 0 ?
                    <li className='list-group-item'>
                        No Messages in This folder.
                    </li> 
                    : null
                }
                {this.state.messages.map((msg, i) =>(
                    <ListItem 
                        msg={msg} 
                        current={this.props.current}
                        setCurrent={this.setCurrent}
                        listIndex={i} />
                ))}

                <li className="list-group-item">
                    <button 
                        className="btn btn-primary"
                        onClick={this.loadMoreMessages}>
                        Load More Emails
                    </button>
                </li>
            </ul>
        )
    }
}

export default DraftList;