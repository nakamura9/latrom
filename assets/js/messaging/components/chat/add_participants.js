import React, {Component} from 'react';
import ReactModal from 'react-modal';
import axios from 'axios';

class ParticipantsWidget extends Component{
    state = {
        data: [],
        selecting: false
    }

    componentDidUpdate(prevProps, prevState){
        if(prevProps.participants != this.props.participants){
            this.setState({data: this.props.participants})
        }
        
    }

    addParticipantsHandler = (id) =>{
        if(this.state.selecting){
            this.setState({selecting:false});
            this.props.addParticipant(id);
        }
    }

    addParticipantButtonHandler =() =>{
        axios({
            'method': 'GET',
            'url': '/base/api/users/'
        }).then(res =>{
            this.setState({
                data: res.data.filter(usr =>{
                    return this.props.participants.map(p =>p.id).indexOf(usr.id) == -1
                }),
                selecting: true

            })
        })
    }

    render(){
        const color = this.state.selecting ? "btn-danger" : "btn-success" 
        const icon = this.state.selecting ? 'times' : 'plus'
        return (
            <ReactModal 
                
                isOpen={this.props.open}
                parentSelector={() => document.getElementById('chat-body')}>
                <button 
                        className="btn btn-danger"
                        onClick={this.props.closeModal}> <i className="fas fa-times"></i></button>
                    
                <div style={{
                    width: "50%",
                    margin: "20px auto"
                }}>
                    <h4>Participants</h4>

                    <ul className="list-group">
                        {this.state.data.map((i) =>(
                            <li 
                                className="list-group-item"
                                onClick={() => this.addParticipantsHandler(i.id)}>{i.username}</li>
                        ))}
                    </ul>
                    <center>
                        <button
                            className={color + " btn-lg btn"}
                            onClick={this.addParticipantButtonHandler}>
                        <i className={"fas fa-" + icon}></i> {this.state.selecting ? "Cancel" : "Add Participant"}
                    </button>
                    </center>
                </div>
            </ReactModal>
        )    
    }
}

export default ParticipantsWidget;