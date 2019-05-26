import React, {Component} from 'react';
import styles from './chatStyles.css';
class chatHeader extends Component {
    state = {
        showDropdown: false
    }
    render(){
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
                            <ul className={styles.chatDropdownUl}>
                                <li className={styles.chatDropdownLi}>Close Chat</li>
                                <li className={styles.chatDropdownLi}>Add attachment</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
            </div>
            
        )
    }
    }
    

export default chatHeader