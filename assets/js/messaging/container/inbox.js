import React, {Component} from 'react';
import styles from './inbox.css';
import FolderList from '../components/email/folder';
import MessageDetail from '../components/email/message_detail';
import axios from 'axios';
import {Aux} from '../../src/common';

const FolderCard = (props) =>{
    return (
        <li style={{
            padding: '5px 3px'
        }}
            className={["list-group-item", 
            props.focused 
                ? 'selected-folder'
                : ''].join(' ')}
            onClick={props.handler}>
            {props.name}
        </li>
    )
}
class InboxView extends Component{
    state = {
        current: null,
        profile: null,
        folder: null,
        folderList: [],
        currentMessage: ''
    }

    syncFolders = () =>{
        this.setState({currentMessage: 'Syncing Email...'})
        axios({
            'url': '/messaging/api/sync-folders/' + this.state.profile,
            'method': 'GET'
        }).then(() =>{
            alert('Emails Synchronized successfully.')
        })
    }

    componentDidMount(){
        const id = document.getElementById('id_profile').value
        const url = `/messaging/api/email-profile/${id}/`
        
        axios({
            method: 'GET',
            url: url
        }).then(res =>{
            this.setState({
                folderList: res.data.folders,
                profile: id
        })
        })
    }

    setCurrent =(id) =>{
        this.setState({
            current: id,
        })
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
        axios.patch('/messaging/api/email/' + id + '/', {'read': true});
    }

    render(){
        return(
            <Aux>
                <div style={{display:'flex', flexDirection:'row'}}>
                    <div className="btn-group">
                        <a href="/messaging/create-message" className="btn btn-primary "> <i className="fas fa-edit    "></i> </a>
                        <button 
                            onClick={this.syncFolders}
                            className="btn btn-primary"> 
                            <i className="fas fa-sync"></i> 
                        </button>
                    </div>
                    <div>{this.state.currentMessage}</div>
                </div>

                <div className={styles.inboxContainer} >
                    
                    <div className={styles.inboxMenu}>
                        
                        <h5 className={styles.headers}>Folders</h5>
                        <ul style={{
                            maxHeight: '300px',
                            overflowY: 'auto'
                        }}
                            className="list-group">
                            {this.state.folderList.map((folder)=>(
                                <FolderCard 
                                    handler={()=>this.setState(
                                        {folder: folder.id}
                                        )}
                                    folderID={folder.id}
                                    name={folder.name}
                                    focused={folder.id === this.state.folder} />
                            ))}
                            
                        </ul>
                    </div>
                    <div className={styles.inboxList}>
                        <h5 className={styles.headers}>List</h5>
                        <FolderList 
                            setCurrent={this.setCurrent}
                            current={this.state.current}
                            folderID={this.state.folder}/>
                    </div>
                    <div className={styles.inboxMessageDetail}>
                        <MessageDetail messageID={this.state.current} draft={true}/>
                    </div>
                </div>
            </Aux>
        )
    }
}

export default InboxView;