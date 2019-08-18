import React, {Component} from 'react';
import styles from '../styles.css';

class Card extends Component{
    state = {
        showOptions: false
    }

    toggleOptions = () =>{
        this.setState((prevState) =>({showOptions: !prevState.showOptions}))
    }

    render(){
        return(
            <div className={styles.timelineCard}
                style={{
                    height: this.state.showOptions ? '200px' : '100px'
                }}>
                <div className={styles.timelineCardLeft}>
                    <div className={styles.timelinePoint}></div>
                </div>
                <div className={styles.timelineCardRight + ' hvr-grow'}>
                    <h6 style={{fontWeight: 200}}>{this.props.timestamp}</h6>
                    <p>{this.props.title}</p>
                            
                    <i onClick={this.toggleOptions} className="fa fa-ellipsis-h" ></i>
                    <div className={styles.cardOptions} style={{
                        display: this.state.showOptions ? 'block' :"none"}}>
                        <a className='dropdown-item' href={"/planner/event-detail/" + this.props.id}> <i className="fas fa-file"></i> View</a>
                        <a className='dropdown-item' href={"/planner/event-update/" + this.props.id}> <i className="fas fa-edit"></i> Edit</a>
                        <a className='dropdown-item' href={"/planner/event-delete/" + this.props.id}> <i className="fas fa-trash"></i> Delete</a>
                            
                    </div>
                </div>
            </div>
        )
    }
}

export default Card;