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
            backgroundColor: "#007bff",
            color: 'white',
            padding: "3px",
            margin: "3px",
            borderRadius: "5px"
            
        };
        return(
            <div style={containerStyle}>
                <ParticipantEntry 
                    dataList={this.state.items}
                    addHandler={this.addHandler}/>
                <div style={{overflowY: 'auto', maxHeight: "200px"}}>
                    {this.state.items.map((item, i) =>{
                        return(<SelectedItem 
                            index={i}
                            key={i}
                            participantType={item.type}
                            handler={this.removeHandler}
                            name = {item.name}/>)
                    })}
                </div>
                
            </div>
        );
    }
}

class ParticipantEntry extends Component{
    state = {
        selecting: "employee",
        next: "",
        selected : {

        }
    }

    clickHandler = (evt) =>{
        //convoluted but working
        //need to momentarily clear the select widgets before loading the next one 
        this.setState({next: evt.target.id}, () =>{
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
        if(!this.state.selected.name){
            alert('No valid participant has been selected.');
            return;
        }
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
            padding: "10px"
        }

        const tabStyle = {
            listStyleType: 'none',
            display: 'inline-block',
            borderRadius: '5px 5px 0px 0px',
            padding: '5px',
            borderStyle: 'solid',
            borderColor: 'white'

        }
        return (
            <div style={divStyle}>
            <ul style={{listStylePosition: 'inside', paddingLeft: '0px'}}>
            <li 
                id="employee" 
                style={{...tabStyle,
                    borderWidth: this.state.selecting ==="employee"
                    ? '1px 1px 0px 1px '
                    : '0px 0px 1px 0px ',}}
                onClick={this.clickHandler}>Employee</li>
            <li 
                id="customer" 
                style={{...tabStyle,
                    borderWidth: this.state.selecting ==="customer"
                    ? '1px 1px 0px 1px '
                    : '0px 0px 1px 0px ',}}
                onClick={this.clickHandler}>Customer</li>
            <li 
                id="supplier" 
                style={{...tabStyle,
                    borderWidth: this.state.selecting ==="supplier"
                    ? '1px 1px 0px 1px '
                    : '0px 0px 1px 0px ',}}
                onClick={this.clickHandler}>Vendor</li>
        </ul>
                <div style={{display: "flex", width: '100%'}}>
                    <div style={{width: "100%"}}>{widgetSelector}</div>
                    <div> <button 
                    className="btn"
                    type="button"
                    onClick={this.insertHandler}>
                        <i className="fas fa-plus"></i>
                    </button></div>
                </div>            
                
            </div>
        );
    }       
}


const SelectedItem = (props) => {
    let divStyle = {
        color: "black",
        backgroundColor: "white",
        margin: "2px",
        padding: "5px",
        borderTop: "1px solid #fff"
    }
    const spanStyle = {
        borderLeft: "1px solid #fff",
        margin: "0px 15px",
        padding: "0px 5px"
    }
    return(
        <div style={divStyle} >
            <DeleteButton 
                index={props.index}
                handler={props.handler}/>
            <span style={spanStyle}>{`[${props.participantType}]: ${props.name}`}</span>   
        </div>
    );
}


export default ParticipantSelectWidget;