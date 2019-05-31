import React from 'react';
import axios from 'axios';

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
                    <li onClick={ () => this.props.setCurrent(msg.id)} className="list-group-item">
                        <h6>{msg.sender}</h6>
                        <p>{msg.subject.substring(0, 25) + '...'}</p>
                    </li>
                ))}
            </ul>
        )
    }
}

export default InboxList;