import React, {Component} from 'react';

class FilePickerUI extends Component {
    state = {
        filename: ""
    }
    fileSelectHandler = () =>{
        let input = document.getElementById(this.props.fieldID);
        input.click();
    }
    
    inputChangeHandler = (evt) =>{
        this.setState({filename: evt.target.files[0].name})
        this.props.fileHandler(evt.target.files[0])
    }

    fileClearHandler = () => {
        let input = document.getElementById(this.props.fieldID);
        input.value = null;
        this.setState({filename: ""})
        this.props.fileHandler(null)
    }
    
    render(){
        return (<div>
            <input 
                type="file" 
                name={this.props.fieldName} 
                id={this.props.fieldID}
                style={{display:"none"}}
                onChange={this.inputChangeHandler} />
            {this.state.filename === "" 
                ? <button 
                        type="button"
                        className="btn btn-primary"
                        onClick={this.fileSelectHandler}>Select File</button>
                : <button 
                        type="button"
                        className="btn btn-primary"
                        onClick={this.fileClearHandler}>
                            {this.state.filename} 
                            <i className="fas fa-times"></i>
                </button>}
            
        </div>)
    }
}

export  default FilePickerUI;