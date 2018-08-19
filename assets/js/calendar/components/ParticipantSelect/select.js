import React, {Component} from 'react';
import {SearchableWidget, DeleteButton} from '../../../src/common';
import $ from 'jquery';
import axios from 'axios';

class ParticipantSelectWidget extends Component{
    state = {
        items: []
    }

    componentDidMount(){
        //prepopulate form
        const decomposed = window.location.href.split('/');
        const tail = decomposed[decomposed.length - 1];
        if(tail !== 'event-create'){
            axios({
                url: '/planner/api/event/' + tail, 
                method: 'GET'
            }).then( res => {
                let items = res.data.participants.map((item, i ) =>{
                    let p = null;
                    switch(item.participant_type){
                        case 2:
                            return({
                                type: 'supplier',
                                pk: item.supplier.id,
                                name: item.supplier.name
                            });
                            break;
                        case 1:
                            return({
                                type: 'customer',
                                pk: item.customer.id,
                                name: item.customer.name
                            });
                            break;
                        case 0:
                            return({
                                type: 'employee',
                                pk: item.employee.employee_number,
                                name: item.employee.first_name
                            });
                            break;
                        default:
                            return {};
                    }
                    
                });
                this.setState({items: items});
            })
        }

        $('<input>').attr({
            type: 'hidden',
            name: 'participants',
            id: 'id_participants',
            value: ""
        }).appendTo('form');
    }

    addHandler = (data) =>{
        let newItems = [...this.state.items];
        newItems.push(data);
        this.setState({items: newItems}, this.updateForm);
    }

    removeHandler = (index) =>{
        let newItems = [...this.state.items];
        newItems.splice(index, 1);
        this.setState({items: newItems}, this.updateForm);
    }

    updateForm = () => {
        $('#id_participants').val(
            encodeURIComponent(
                JSON.stringify(this.state.items)));
    } 

    render(){
        
        return(
            <div>
                <h3>Select Participants</h3>
                <div>
                    {this.state.items.map((item, i) =>{
                        return(<SelectedItem 
                            index={i}
                            key={i}
                            handler={this.removeHandler}
                            name = {item.name}/>)
                    })}
                </div>
                <ParticipantEntry addHandler={this.addHandler}/>
            </div>
        );
    }
}

class ParticipantEntry extends Component{
    state = {
        selecting: "",
        selected : {

        }
    }
    radioHandler = (evt) =>{
        this.setState({selecting: evt.target.value});
    }

    onClearHandler = () =>{
        this.setState({selected: {}});
    }

    onSelectHandler = (str) =>{
        let pk = null;
        let name = null;
        [pk, name] = str.split('-');
        this.setState({selected: {
            type: this.state.selecting,
            pk: pk,
            name: name
        }});
    }

    insertHandler = () =>{
        // reset the selecting widget to prevent errors in the select widget
        this.setState({selecting: ""}, () => 
            this.props.addHandler(this.state.selected)
    );
        
    }
    render(){
            let widgetSelector = null;
            
            switch(this.state.selecting){
                case 'employee':
                    widgetSelector = <SearchableWidget 
                        dataURL="/employees/api/employee/"
                        idField="employee_number"
                        displayField="first_name" //change to full name
                        onClear={this.onClearHandler}
                        onSelect={this.onSelectHandler} />
                    break;
                case 'customer': 
                    widgetSelector = <SearchableWidget
                        dataURL="/invoicing/api/customer/"
                        idField="id"
                        displayField="name"
                        onClear={this.onClearHandler}
                        onSelect={this.onSelectHandler} />
                    break;
                case 'supplier': //supplier
                    widgetSelector = <SearchableWidget 
                        dataURL="/inventory/api/supplier/"
                        idField="id"
                        displayField="name"
                        onClear={this.onClearHandler}
                        onSelect={this.onSelectHandler} />
                    break;
                default:
                    widgetSelector = <h4>Select Participant Category</h4>
            }
        const divStyle = {
            border: "1px solid #ddd",
            padding: "10px"
        }
        return (
            <div style={divStyle}>
                <RadioGroup handler={this.radioHandler}/>
                <div style={{margin: "8px 0"}}>
                    {widgetSelector}
                </div>            
                <button 
                    className="btn btn-primary"
                    onClick={this.insertHandler}>
                        Add Participant
                    </button>
            </div>
        );
    }       
}

const RadioGroup = (props) =>{
    return(
        <div>
            <label 
            className="radio-inline" 
            style={{marginLeft: "30px"}}>
            <input 
                type="radio" 
                name="selecting"
                value="employee"
                onChange={props.handler} />Employee
        </label>
        <label 
            className="radio-inline" 
            style={{marginLeft: "30px"}}>
            <input 
                type="radio" 
                name="selecting"
                value="customer"
                onChange={props.handler} />Customer
        </label>
        <label 
            className="radio-inline" 
            style={{marginLeft: "30px"}}>
            <input 
                type="radio" 
                name="selecting"
                value="supplier"
                onChange={props.handler} />Supplier
        </label>
        </div>
    );
}

const SelectedItem = (props) => {
    let divStyle = {
        margin: "2px",
        padding: "5px",
        border: "1px solid #ddd"
    }
    const spanStyle = {
        borderLeft: "2px solid #ddd",
        margin: "0px 15px",
        padding: "0px 5px"
    }
    return(
        <div style={divStyle}>
            <DeleteButton 
                index={props.index}
                handler={props.handler}/>
            <span style={spanStyle}>{props.name}</span>   
        </div>
    );
}


export default ParticipantSelectWidget;