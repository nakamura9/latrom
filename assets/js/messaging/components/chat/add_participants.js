import React, {Component} from 'react';
import ReactModal from 'react-modal';
import axios from 'axios';

const UserCard = (props) =>{
    
    
    if(props.selecting){
        return(
            <li onClick={() => props.handler(props.data.id)}
                className="list-group-item">
                {props.data.username}
            </li>
        )
    }else{
        
        

        return(
            <li className="list-group-item">
                    <button 
                        className="btn btn-danger btn-sm"
                        onClick={() =>{
                            if(confirm(`Are you sure you want to remove ${props.data.username} from the group?`)){
                                props.delHandler(props.data.id)                
                            }}}>
                            <i className="fas fa-trash"></i>
                        </button>
                    {props.data.username}
            </li>
        )
    }
    
}

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
        if(this.state.selecting){
            this.setState({
                selecting: false,
                data: this.props.participants
            });
            return;
        }
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
                            <UserCard 
                                selecting={this.state.selecting}
                                data={i}
                                handler={this.addParticipantsHandler}
                                delHandler={this.props.removeParticipant} />
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