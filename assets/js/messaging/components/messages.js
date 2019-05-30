import React from 'react';
import axios from 'axios';

class InboxList extends React.Component{
    state = {
        messages: [
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
            {sender: 'caleb', subject: 'subject', id: 1},
        ]
    }
    componentDidMount(){
        //axios.get()
    }

    render(){
        return(
            <ul className="list-group">
                {this.state.messages.map((msg, i) =>(
                    <li onClick={ () => this.props.setCurrent(msg.id)} className="list-group-item">
                        <h6>{msg.sender}</h6>
                        <p>{msg.subject}</p>
                    </li>
                ))}
            </ul>
        )
    }
}

export default InboxList;