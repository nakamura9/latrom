import React from 'react';
import axios from 'axios';
import ListItem from './message_list_item';

class InboxList extends React.Component{
    state = {
        messages: [
            
        ],
        status: 'loading'
    }
    componentDidMount(){
        axios.get('/messaging/api/inbox/').then(res =>{
            this.setState({
                messages: res.data,
                status: 'loaded'
            })
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
                        {this.state.status === 'loaded' ? 'No Messages in this folder'
                            : <img src="/static/common_data/images/spinner.gif" width={50} height={50} />}
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