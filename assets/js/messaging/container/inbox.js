import React, {Component} from 'react';
import styles from './inbox.css';
import InboxList from '../components/messages';
import DraftList from '../components/drafts';
import SentList from '../components/sent';
import MessageDetail from '../components/message_detail';

class InboxView extends Component{
    state = {
        view: 'inbox',
        current: null
    }

    setCurrent =(id) =>{
        this.setState({current: id})
    }

    render(){
        let renderedList;
        switch(this.state.view){
            case 'inbox':
                renderedList = <InboxList setCurrent={this.setCurrent} />;
                break;
            case 'drafts':
                renderedList = <DraftList setCurrent={this.setCurrent}/>;
                break;

            case 'sent':
                renderedList = <SentList setCurrent={this.setCurrent}/>;
                break;

            default:
                console.log(this.state.view)
                renderedList = <InboxList setCurrent={this.setCurrent}/>;
        }

        

        return(
            <div className={styles.inboxContainer} >
                <div className={styles.inboxMenu}>
                    <h5 className={styles.headers}>Folders</h5>
                    <ul className="list-group">
                        <li 
                            className="list-group-item"
                            onClick={()=>this.setState({view: 'inbox'})}
                            >
                            Inbox
                        </li>
                        <li 
                            className="list-group-item"
                            onClick={()=>this.setState({view: 'drafts'})}
                            >
                            Drafts
                        </li>
                        <li 
                            className="list-group-item"
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
                    <MessageDetail messageID={this.state.current}/>
                </div>
            </div>
        )
    }
}

export default InboxView;