import React, { Component } from 'react';
import InputLine from '../components/input_line';
import TitleBar from '../components/title_bar';
import DataRow from '../components/row';
import Totals from '../../components/totals_table';
import axios from 'axios';

/**
 * fieldOrder -array of strings 
 * formInputID - string used to find the hidden input that updates the form
 * fields - array of objects 
 * prepopulated - boolean for update views 
 * urlFetcher - a function that returns the url with the prepoulation url
 * resProcessor - a function which maps the fetched data onto the lines array
 * taxFormField - a string representing the id of the tax field if required for 
 * totals
 * calculateTotal - function used to add cumulative total for tables with total fields( takes a rows data and returns a number that represents the total for that row)
 * fieldDescriptions - headings used at the top of fields, in order
 * NB please supply a lineTotal for the fields that require it
 */

 /**
  * fields object must have at least a name property,
  * a type property which is one of ('select', text', 'number', 'search', 
  * 'fetch')
  * only one search and fetch field allowed per table 
  * and a width property, the sum for all fields must be 90
  * 
  * for search widgets additional fields must be supplied
  * url - the url to fetch the data string
  * idField - the name of the id for the fetched data string
  * canCreateNewItem - bool
  * displayField - the field to be listed for selection string
  * newLink - if canCreateNewItem is true the url for creating new things
  * 
  */

class GenericTable extends Component{
    state = {
        lines: []
    }

    componentDidMount = () => {
        //for update views
        //come up with a common check for update views

        if(this.props.prepopulated){
            const url = this.props.urlFetcher();
            axios.get(url)
                .then(res => {
                    this.setState({lines: this.props.resProcessor(res)})
                });
        }
    }

    taxChangeHandler = (id) =>{
        document.getElementById('id_tax').value = id;
    }

    dataRowDeleteHandler = (index) =>{
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, this.updateForm);
    }

    insertHandler = (data) =>{
        let i= 0;
        let field = null;
        let fieldName = null;
        let value = ""
        for(i in this.props.fieldOrder){
            fieldName = this.props.fieldOrder[i];
            field = this.props.fields[i];
            value = data[fieldName]
            if(field.required && value === ""){
                alert(`A required field, ${fieldName} is missing.`);
                return;
            } 
        }
        let newLines = [...this.state.lines];
        newLines.push(data);
        this.setState({lines: newLines}, this.updateForm);
    }

    updateForm = () =>{
        let field = document.getElementById(this.props.formInputID);
        if(field){
            field.value =
            encodeURIComponent(
                JSON.stringify(this.state.lines)
                );
        }
        
    }
    render(){
        return(
            <table className="table table-sm">
                
                <TitleBar 
                    fieldOrder={this.props.fieldDescriptions}
                    fields={this.props.fields}
                    hasLineTotal={this.props.hasLineTotal}/>
                <tbody>
                    {this.state.lines.map((field, i) =>(
                        <DataRow 
                            key={i}
                            data={this.state.lines[i]}
                            fieldOrder={this.props.fieldOrder}
                            index={i}
                            hasLineTotal={this.props.hasLineTotal}
                            deleteHandler={this.dataRowDeleteHandler}/>
                    ))}
                </tbody>
                <InputLine 
                    hasLineTotal={this.props.hasLineTotal}
                    fieldOrder={this.props.fieldOrder}
                    insertHandler={this.insertHandler}
                    fields={this.props.fields}
                    calculateTotal={this.props.calculateTotal}
                    lines={this.state.lines}/>
                {this.props.hasTotal 
                ?   <Totals 
                        span={this.props.fields.length + 2}
                        list={this.state.lines}
                        taxFormField={this.props.taxFormField}
                        subtotalReducer={function(x, y){
                            return (x + parseFloat(y.lineTotal));
                        }}/>
                :   null}
                
            </table>
        )
    }
}

export default GenericTable;