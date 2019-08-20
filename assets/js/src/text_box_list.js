import React, {Component} from 'react';
import $ from 'jquery';
import axios from 'axios';

class TextBoxListWidget extends Component{
    state = {
        value: "",
        items: [],
        selected: null
    }

    componentDidMount(){
        $('<input>').attr({
            name: this.props.fieldName,
            type: 'hidden',
            id: 'id_' + this.props.fieldName,
            value: encodeURIComponent(JSON.stringify(
                []
            ))

        }).appendTo('form');

        // get prepopulated data 
        axios({
            url: this.props.populatedURL,
            method: "GET"
        }).then(res =>{
            const dataList = this.props.resProcessor(res)
            this.setState({items: dataList}, this.updateForm)
        })
    }

    addHandler = () => {
        let newItems = [...this.state.items];
        if(this.state.selected !== null){
            newItems[this.state.selected] = this.state.value;
        }else{
            newItems.push(this.state.value);
        }
        this.setState({
            items: newItems,
            value: "",
            selected: null
        }, this.updateForm);

    }

    updateForm = () =>{
        $('#id_' + this.props.fieldName).val(encodeURIComponent(JSON.stringify(this.state.items)));
    }

    removeHandler = (index) => {
        let newItems = [...this.state.items];
        newItems.splice(index, 1);
        this.setState({items: newItems}, this.updateForm);
    }
    
    editHandler = (index) =>{
        this.setState({
            value: this.state.items[index],
            selected: index
        }, this.updateForm) 
    }
    inputHandler = (evt) =>{
        this.setState({value: evt.target.value});
    }

    render(){
        const containerStyle= {
            display: "block",
            'color': "black",
            clear: 'both',
            width: "100%",
            backgroundColor: "white",
            borderRadius: "5px",
            padding: "15px",
            margin: "5px"
        };
        const textAreaStyle = {
            width: '100%', 
            borderRadius: "5px", 
            padding: "3px"};
        return(
            <div style={containerStyle}>
                <div style={{maxHeight: "350px", overflowY: 'auto'}}>
                    <h4>{this.props.title}</h4>
                    {this.state.items.map((item, i) => {
                        return(<ListTextBox 
                            text={item} 
                            key={i}
                            index={i}
                            editHandler={this.editHandler}
                            handler={this.removeHandler}/>
                    )})}
                </div>
                <div>
                    <label>
                        Enter Text below...
                    </label>
                    <br />
                    <textarea 
                        style={textAreaStyle}
                        name="textInput"
                        rows={4}
                        value={this.state.value}
                        onChange={this.inputHandler}></textarea>
                        <br />
                    <button 
                        className="btn"
                        type="button"
                        onClick={this.addHandler}>Insert</button>
                </div>
            </div>
        );
    }
}

const ListTextBox = (props) => {
    const containerStyle = {
        width: "90%",
        margin: "10px auto",
        borderBottom: "2px solid white",
        padding: "10px",
    };


    const buttonStyle ={
        color: "#007bff",
        border: "0px",
        backgroundColor: "rgba(0,0,0,0)"
    }
    return(
        <div style={containerStyle}>
            <div >
                <div >
                    <span style={{float: "left"}}>{props.index + 1}.</span>
                    <span style={{float: "right"}}>
                        <button 
                        style={buttonStyle}
                        type="button"
                        onClick={() => props.handler(props.index)}>
                            <i className="fas fa-times"></i>
                        </button>
                        <button 
                        style={buttonStyle}
                        type="button"
                        onClick={() => props.editHandler(props.index)}>
                            <i className="fas fa-edit"></i>
                        </button>
                    </span>
                </div>        
            </div>
            <div style={{clear: "both"}}>{props.text}</div>
        </div>
    );
}

export default TextBoxListWidget;