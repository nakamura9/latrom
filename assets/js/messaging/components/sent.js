import React from 'react';
import axios from 'axios';

class SentList extends React.Component{
    state = {
        messages: [{sender: 'caleb', recipient:'recipient', subject: 'subject', id: 1}]
    }
    componentDidMount(){
        //axios.get()
    }
    render(){
        return(
            <ul className="list-group">
                {this.state.messages.map((msg, i) =>(
                    <li className="list-group-item">
                        <h6>{msg.recipient}</h6>
                        <p>{msg.subject}</p>
                    </li>
                ))}
            </ul>
        )
    }
}

export default SentList;