import React from 'react';
import axios from 'axios';
import ListItem from './message_list_item';

class InboxList extends React.Component{
    state = {
        messages: [
            
        ]
    }
    componentDidMount(){
        axios.get('/messaging/api/inbox/').then(res =>{
            this.setState({messages: res.data})
        })
    }

    setCurrent = (id, index) =>{
        let newMessages = [...this.state.messages];
        let newMsg = newMessages[index];
        newMsg.read = true;
        newMessages[index] = newMsg;
        this.setState({messages: newMessages})
        this.props.setCurrent(id, false);
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
            </ul>
        )
    }
}

export default InboxList;