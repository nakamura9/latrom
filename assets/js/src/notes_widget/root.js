import React, {Component} from 'react';
import AsyncSelect from '../components/async_select';
import {setDataPayload} from '../utils';
import axios from 'axios';

/**
 * Props 
 * token - csrfmiddlewaretoken string
 * target - string representation of the model that will accept the note. 
 *             the string must be registered in the targets dictionary in  the 
 *              server
 * targetID - pk of the specific object receiving the notes
 */

class NotesWidget extends Component{
    state = {
        author: null,
        note: "",
        notesList: []
    }

    inputHandler = (evt) =>{
        this.setState({note: evt.target.value});
    }

    selectWidgetHandler = (value) =>{
        this.setState({author: value});
    }

    submitHandler = () =>{
        
        axios({
            'method': 'POST',
            'url': '/base/create-note',
            'data': setDataPayload({
                'csrfmiddlewaretoken': this.props.token,
                'target': this.props.target,
                'target_id': this.props.targetID,
                ...this.state
            })
        }).then(()=>{
            let newNotes = [...this.state.notesList];
            newNotes.push({note: this.state.note, author: this.state.author})
            this.setState({
                note: "",
                notesList: newNotes
            });
        });
          
    }

    componentDidMount(){
        if(this.props.dataURL){
            axios({
                method: 'get',
                'url': this.props.dataURL,
            }).then((res) =>{
                this.setState({notesList: res.data})
            })
            //get the list of notes for a given document

        }
    }

    render(){
        const containerStyle ={
            margin: "5px",
            padding: "10px",
            borderRadius: "5px",
            backgroundColor: "#007bff",
            color: 'white'
        };
        const notesListStyle = {
            maxHeight: '400px',
            overflowY: 'auto'
        }

        return(<div style={containerStyle}>
            <div className="notes-list" 
                style={notesListStyle}>
                <ul className="list-group">
                    {this.state.notesList.map((note) =>(
                        <Note {...note} />
                    ))}
                </ul>
            </div>
            <div className="form-group">
              <label >Author:</label>
              <AsyncSelect 
                dataURL="/base/api/users"
                handler={this.selectWidgetHandler}
                name="author"
                resProcessor={(res)=>{
                    return res.data.map((item)=>({
                        name: item.username,
                        value: item.id
                    }))
                }}/>
              <label >Note:</label>
              <textarea 
                className="form-control" 
                id="note-widget" rows="3"
                onChange={this.inputHandler}
                value={this.state.note}></textarea>
            </div>
            {/* May eliminate this button, Make a prop? */}
            <button onClick={this.submitHandler} type="button" className="btn">Submit</button>
        </div>)
    }
}

class Note extends Component{
    state = {
        authorString: ''
    }

    componentDidMount(){
        axios({
            'method': 'GET',
            'url': '/base/api/users/'+ this.props.author
        }).then((res)=>{
            this.setState({authorString: res.data.username})
        })
    }

    render(){
        return(
            <li className='list-group-item' 
                style={{
                    'color': 'black'
                }}>
                <strong>{this.state.authorString}: </strong>
                {this.props.note}
            </li>
        )
    }
}


export default NotesWidget;