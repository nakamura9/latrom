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
        return(
            <div style={{
                display: "block",
                clear: 'both',
                width: "350px"
            }}>
                <div>
                    <h3>{this.props.title}</h3>
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
                        Enter Text Here
                    </label>
                    <br />
                    <textarea 
                        style={{width: '100%'}}
                        name="textInput"
                        rows={5}
                        value={this.state.value}
                        onChange={this.inputHandler}></textarea>
                        <br />
                    <button 
                        className="btn"
                        onClick={this.addHandler}>Insert</button>
                </div>
            </div>
        );
    }
}

const ListTextBox = (props) => {
    return(
        <div style={{
            width: "90%",
            margin: "10px auto",
            border: "1px solid black",
            padding: "10px"
        }}>
            <div style={{
                display: "block",
                clear: "both"
            }}>
                <span style={{float: "left"}}>{props.index + 1}.</span>
                <span style={{float: "right"}}>
                    <button 
                    className="btn"
                    onClick={() => props.handler(props.index)}>
                        <i className="fas fa-times"></i>
                    </button>
                    <button 
                    className="btn"
                    onClick={() => props.editHandler(props.index)}>
                        <i className="fas fa-edit"></i>
                    </button>
                </span>        
            </div>
            <div style={{
                display: "block",
                clear: "both"
            }}>{props.text}</div>
        </div>
    );
}

export default TextBoxListWidget;