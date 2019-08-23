import React, {Component} from 'react';
import styles from './chatStyles.css';
import {Aux} from '../../../src/common';

class chatHeader extends Component {
    state = {
        showDropdown: false
    }

    addAttachment = () =>{
        let input =  document.getElementById('attachment');
        input.click();
    }

    
    render(){

        let rendered = null;
        if(this.props.selecting){
            rendered= (
                <Aux>
                    <li 
                        className={styles.chatDropdownLi}
                        onClick={this.props.toggleUsersModal}>
                            Forward Selected</li>
                    <li 
                        className={styles.chatDropdownLi}
                        onClick={this.props.deleteHandler}>Delete Selected</li>
                </Aux>
                )
        }
        return(
            <div>
                <div className="col-sm-12 bg-primary text-white" 
                    style={{padding: "10px"}}>
                    <h3 style={{
                        display: "inline-block"
                    }}>{this.props.title}</h3>

                    
                    <div style={{
                        'float': 'right',
                        display: "inline-block"
                    }}>
                        <button 
                            className='btn'
                            onClick={() => {
                                this.setState({
                                showDropdown: !this.state.showDropdown}
                                )}}>
                                <i className="fas fa-ellipsis-v"></i></button>
                        <div className={["shadow", styles.chatDropdown].join(" ")} style={{
                            display: this.state.showDropdown ? 'block' : 'none',
                        }}>
                            <input 
                                type="file" 
                                 style={{display: 'none'}}
                                id="attachment"
                                onChange={this.props.attachmentHandler} />
                            <ul className={styles.chatDropdownUl}>
                                <li className={styles.chatDropdownLi}> <a href={this.props.isGroup
                                    ? "/messaging/close-group/" + this.props.chatID
                                    :"/messaging/close-chat/" + this.props.chatID}> Close {this.props.isGroup ? 'Group' : 'Chat'}</a></li>
                                <li className={styles.chatDropdownLi}
                                    onClick={this.addAttachment}>Add attachment</li>
                                <li className={styles.chatDropdownLi}
                                    onClick={this.props.toggleContext}>{this.props.selecting ? 
                                        'Clear' : 
                                        'Select'} Messages</li>
                                {this.props.isGroup ?
                                    <li className={styles.chatDropdownLi}
                                        onClick={() => {
                                            this.setState({showDropdown: false})
                                            this.props.toggleParticipants()}
                                        }>View Participants</li> : null}
                                {rendered}
                            </ul>
                        </div>
                    </div>
                </div>
                
            </div>
            
        )
    }
    }
    

export default chatHeader