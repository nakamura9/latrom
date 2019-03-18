import React, {Component} from 'react';
import SearchableWidget from '../../../src/components/searchable_widget';
import $ from 'jquery';
import axios from 'axios';
import {DeleteButton} from "../../../src/common";

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
        $('#id_json_participants').val(
            encodeURIComponent(
                JSON.stringify(this.state.items)));
    } 

    render(){
        const containerStyle = {
            backgroundColor: "#9cd",
            padding: "20px",
            margin: "5px",
            borderRadius: "20px"
            
        };
        return(
            <div style={containerStyle}>
                <h4>Select Participants</h4>
                <div>
                    {this.state.items.map((item, i) =>{
                        return(<SelectedItem 
                            index={i}
                            key={i}
                            handler={this.removeHandler}
                            name = {item.name}/>)
                    })}
                </div>
                <ParticipantEntry 
                    dataList={this.state.items}
                    addHandler={this.addHandler}/>
            </div>
        );
    }
}

class ParticipantEntry extends Component{
    state = {
        selecting: "",
        next: "",
        selected : {

        }
    }
    radioHandler = (evt) =>{
        //convoluted but working
        //need to momentarily clear the select widgets before loading the next one 
        this.setState({next: evt.target.value}, () =>{
            this.setState({selecting: ""}, () =>{
                this.setState({selecting: this.state.next});
            })
        });
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
        this.props.addHandler(this.state.selected);
    }
    render(){
            let widgetSelector = null;
            
            switch(this.state.selecting){
                case 'employee':
                    widgetSelector = <div>
                    <SearchableWidget 
                    list={this.props.dataList}
                    dataURL="/employees/api/employee/"
                    idField="employee_number"
                    displayField="first_name" //change to full name
                    onClear={this.onClearHandler}
                    onSelect={this.onSelectHandler} />
                    </div>
                    break;
                case 'customer': 
                    widgetSelector = <div>
                    <SearchableWidget
                    list={this.props.dataList}
                    dataURL="/invoicing/api/customer/"
                    idField="id"
                    displayField="name"
                    onClear={this.onClearHandler}
                    onSelect={this.onSelectHandler} />
                    </div>
                    break;
                case 'supplier': //supplier
                    widgetSelector = <div>
                    <SearchableWidget 
                    list={this.props.dataList}
                    dataURL="/inventory/api/supplier/"
                    idField="id"
                    displayField="name"
                    onClear={this.onClearHandler}
                    onSelect={this.onSelectHandler} />
                    </div>
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