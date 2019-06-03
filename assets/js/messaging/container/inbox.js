import React, {Component} from 'react';
import styles from './inbox.css';
import InboxList from '../components/email/inbox';
import DraftList from '../components/email/drafts';
import SentList from '../components/email/sent';
import MessageDetail from '../components/email/message_detail';
import axios from 'axios';

class InboxView extends Component{
    state = {
        view: 'inbox',
        draft: false,
        current: null
    }

    setCurrent =(id, draft) =>{
        this.setState({
            current: id,
            draft: draft
        })
        axios.defaults.xsrfCookieName = "csrftoken";
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
        axios.patch('/messaging/api/email/' + id + '/', {'read': true});
    }

    render(){
        let renderedList;
        switch(this.state.view){
            case 'inbox':
                renderedList = <InboxList 
                                    setCurrent={this.setCurrent}
                                    current={this.state.current} />;
                break;
            case 'drafts':
                renderedList = <DraftList 
                                    setCurrent={this.setCurrent}
                                    current={this.state.current}/>;
                break;

            case 'sent':
                renderedList = <SentList 
                                    setCurrent={this.setCurrent}
                                    current={this.state.current}/>;
                break;

            default:
                renderedList = <InboxList setCurrent={this.setCurrent}/>;
        }

        

        return(
            <div className={styles.inboxContainer} >
                <div className={styles.inboxMenu}>
                    <h5 className={styles.headers}>Folders</h5>
                    <ul className="list-group">
                        <li 
                            className={["list-group-item", 
                                        this.state.view === 'inbox' 
                                            ? 'selected-folder'
                                            : ''].join(' ')}
                            onClick={()=>this.setState({view: 'inbox'})}
                            >
                            Inbox
                        </li>
                        <li 
                            className={["list-group-item", 
                            this.state.view === 'drafts' 
                                ? 'selected-folder'
                                : ''].join(' ')}
                            onClick={()=>this.setState({view: 'drafts'})}
                            >
                            Drafts
                        </li>
                        <li 
                            className={["list-group-item", 
                            this.state.view === 'sent' 
                                ? 'selected-folder'
                                : ''].join(' ')}
                            onClick={()=>this.setState({view: 'sent'})}
                        >
                            Sent Items
                        </li>
                    </ul>
                </div>
                <div className={styles.inboxList}>
                    <h5 className={styles.headers}>List</h5>
                    {renderedList}
                </div>
                <div className={styles.inboxMessageDetail}>
                    <MessageDetail messageID={this.state.current} draft={this.state.draft}/>
                </div>
            </div>
        )
    }
}

export default InboxView;