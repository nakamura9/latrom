import React from 'react';
import axios from 'axios';
import ListItem from './message_list_item';

class FolderList extends React.Component{
    state = {
        messages: [
            
        ],
        status: 'loading',
        currentPage: 1
    }
    componentDidUpdate(prevProps, PrevState){
        if(!this.props.folderID){
            return;
        }else if(this.props.folderID != prevProps.folderID){
            console.log('folder selected')
            axios.get('/messaging/api/folder/' +this.props.folderID).then(res =>{
                this.setState({
                    messages: res.data,
                    status: 'loaded'
                })
            })
        }
        
    }

    loadMoreMessages = () =>{
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
        
        axios.get('/messaging/api/folder/' + this.props.folderID, {
            params: {
                page: this.state.currentPage + 1
            }
    }).then( res =>{
            this.setState(prevState => ({
                currentPage: prevState.currentPage + 1,
                messages: prevState.messages.concat(res.data) 
            }))
        }).catch(error =>{
            alert('No more email messages')
        })
    }

    setCurrent = (id, index) =>{
        let newMessages = [...this.state.messages];
        let newMsg = newMessages[index];
        newMsg.read = true;
        newMessages[index] = newMsg;
        this.setState({messages: newMessages})
        this.props.setCurrent(id);
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

export default FolderList;