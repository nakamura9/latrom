import React, {Component} from 'react';
import axios from 'axios';
import TitleBar from '../components/title_bar';
import Row from '../components/row';
import setMultipleAttrs from '../../utils';
/**
 * the mutable table does not have any input lines
 * it has a prepolulated list of items with one or more fields that 
 * can be modified.
 * 
 * Props 
 * formHiddenFieldName - string 
 * headings- array of strings
 * fields -array of objects in the form of:
 *  {
 *      name: <>,
 *      mutable: <>,
 *  }  
 *  dataURL -string for fetching the table
 *  resProcessor - a function that takes axios data as an argument and 
 *  returns an array based on that data
 * 
 */


class MutableTable extends Component{
    state = {
        data: []
    }

    componentDidMount(){
        let form = document.forms[0];

        let input = document.createElement("input");
        setMultipleAttrs(input, {
            'type': 'hidden',
            'name': this.props.formHiddenFieldName,
            'value': '',
            'id': `id_${this.props.formHiddenFieldName}`
        })
        form.appendChild(input);

        axios({
            'url': this.props.dataURL,
            'method': 'GET'
        }).then(res =>{
            this.setState({data: this.props.resProcessor(res)})
        });
    }

    updateForm = () =>{
        let input = document.getElementById(`id_${this.props.formHiddenFieldName}`);
        const formValue = encodeURIComponent(JSON.stringify(
            this.state.data));
        input.setAttribute('value', formValue);         
    }
    inputHandler = (evt) =>{
        const inputComponents = evt.target.name.split("__");
        const rowID = inputComponents[0];
        const fieldName = inputComponents[1];

        let newData = [...this.state.data];
        let newField = newData[rowID];
        newField[fieldName] = evt.target.value; 
        newData[rowID] = newField;

        this.setState({data: newData}, this.updateForm);
    }

    render(){
        return(
            <div>
                <table className="table">
                <TitleBar headings={this.props.headings}/>          
                    <tbody>
                        {this.state.data.map((fieldData, i) =>(
                            <Row
                                key={i}
                                fieldData={fieldData}
                                fields={this.props.fields}
                                rowID={i}
                                inputHandler={this.inputHandler}/>
                        ))}
                    </tbody>
                </table>
            </div>
            )
    }
}

export default MutableTable;