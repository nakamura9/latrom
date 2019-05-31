import React from 'react';
import axios from 'axios';

class SentList extends React.Component{
    state = {
        messages: [{sender: 'caleb', recipient:'recipient', subject: 'subject', id: 1}]
    }
    componentDidMount(){
        axios.get('/messaging/api/sent/').then(res =>{
            this.setState({messages: res.data})
        });
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
                    <li className="list-group-item"
                    onClick={ () => this.props.setCurrent(msg.id)}>
                        <h6>{msg.to}</h6>
                        <p>{msg.subject.substring(0, 25) + '...'}</p>
                    </li>
                ))}
            </ul>
        )
    }
}

export default SentList;