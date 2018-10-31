import React, {Component} from 'react';
import $ from 'jquery';
import {Totals, DeleteButton, SearchableWidget} from '../src/common';
import axios from 'axios';
export default class ServiceLineTable extends Component{
    state = {
            lines: [],
        } 
    
    componentDidMount(){
        $('<input>').attr({
            name:'item_list',
            id: 'id_item_list',
            type: 'hidden'
        }).appendTo('form');
        
        $.ajax({
            'url': '/invoicing/api/config/1',
            'method': 'GET'
        }).then(
            res => {
                this.setState({taxRate: parseFloat(res.sales_tax.rate)});
            }
        );
        //check if the page is an update
        let URL = window.location.href;
        let decomposed = URL.split('/');
        let tail = decomposed[decomposed.length - 1];
        if(tail !== 'create-service-invoice'){
            axios({
                url: '/invoicing/api/service-invoice/' + tail,
                method: 'GET',
            }).then(res =>{
                let itemList = res.data.serviceinvoiceline_set.map((line) =>{
                    return {
                        id: line.service.id,
                        name: line.service.name,
                        rate: line.service.hourly_rate,
                        hours: line.hours,
                        fixedFee: line.service.flat_fee,
                        total: (parseFloat(line.service.hourly_rate) * 
                            parseFloat(line.hours)) + parseFloat(line.service.flat_fee)
                    }
                })
                this.setState({lines: itemList});
            });
        }
    }
    
    insertLine = (data) =>{
        let pk = data['service'].split('-')[0];
        $.ajax({
            url: '/services/api/service/'+ pk,
            method: 'GET'
        }).then(res =>{
            let newLines = [...this.state.lines];
            let line = {
                id: res.id,
                name: res.name,
                rate: res.hourly_rate,
                fixedFee: res.flat_fee,
                hours: data.hours,
                total: parseFloat(res.flat_fee) + (parseFloat(res.hourly_rate) * parseFloat(data.hours))
            };
            newLines.push(line);
            this.setState({lines: newLines}, () => {
                this.updateForm();
            });
        });
    }

    removeLine =(index) =>{
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, ()=>{
            this.updateForm();
        });
    }


    updateForm = () =>{
        $('#id_item_list').val(
            encodeURIComponent(
                JSON.stringify(this.state.lines)
            )
        );
    }

    render(){
        return(
            <table>
                <thead>
                    <tr className="bg-primary text-white">
                        <th></th>
                        <th>Service</th>
                        <th>Rate</th>
                        <th>Hours</th>
                        <th>Line Total</th>
                    </tr>
                </thead>
                <tbody>
                {this.state.lines.map((line, i) => (
                    <ServiceLine 
                        index={i}
                        key={i}
                        line={line}
                        handler={this.removeLine}/>
                ))}
                <EntryRow 
                    itemList={this.state.lines}
                    insertLine={this.insertLine}/>
                </tbody>
                <Totals 
                    span={5}
                    list={this.state.lines}
                    subtotalReducer={function(x, y){
                        return(x + y.total);
                    }}/>
            </table>
        );
    }
}

const ServiceLine = (props) => {
    return(<tr>
        <td>
            <DeleteButton 
                index={props.index}
                handler={props.handler}/>
        </td>
        <td>{props.line.name} + Fixed fee: ${props.line.fixedFee} </td>
        <td>{props.line.rate}</td>
        <td>{props.line.hours}</td>
        <td>{props.line.total.toFixed(2)}</td>
    </tr>);
}

class EntryRow extends Component{
    
    state = {
            currentRate : 0.00,
            services: [],
            inputs: {
                service: '',
                hours: ''
            }
        }
    
    componentDidMount(){
        $.ajax({
            url: '/services/api/service/',
            method: 'GET'
        }).then(res => {
            this.setState({services: res});
        });
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                inputs: {
                    service: '',
                    hours: ''
                }
            })
            //remove selected choice from list of choices 
        }
    }

    handleServiceChange = (evt) =>{
        // first check if the service is in the list

        let newInputs = this.state.inputs;
        newInputs['service'] = evt.target.value;
        this.setState({inputs: newInputs});

        //set the rate of the service
        let pk = evt.target.value.split('-')[0];
        $.ajax({
            url: '/services/api/service/'+ pk,
            method: 'GET'
        }).then(res =>{
            this.setState({currentRate: res.hourly_rate});
        });
    }

    handleHoursChange = (evt) => {
        let newInputs = this.state.inputs;
        newInputs['hours'] = evt.target.value;
        this.setState({inputs: newInputs});
    }
    handleButtonClick = () => {
        if(this.state.inputs.hours < 0.0 || this.state.inputs.hours === ""){
            alert('Please enter a valid quantity');
            return;
        }
        this.props.insertLine(this.state.inputs)
        this.setState({inputs: {
            service: '',
            hours: ''
        }, 
        currentRate:0.00});
    }
    onSelect = (value) =>{
        let newInputs = {...this.state.inputs};
        newInputs['service'] = value;
        this.setState({inputs: newInputs});
        const decomposed = value.split('-')[0];
        const pk = decomposed[0];
        $.ajax({
            url: '/services/api/service/'+ pk,
            method: 'GET'
        }).then(res =>{
            this.setState({currentRate: res.hourly_rate});
        });

    }

    onClear = () =>{
        this.setState({inputs: {
            service: '',
            hours: ''
        }})
    }
    
    render(){
        return(
                <tr>
                    <td style={{width: "10%"}}></td>
                    <td style={{width: "50%"}}>
                        <SearchableWidget
                            list={this.props.itemList}
                            dataURL="/services/api/service/"
                            displayField="name"
                            idField="id"
                            onClear={this.onClear}
                            onSelect={this.onSelect}/>
                    </td>
                    <td style={{width: "10%"}}>{this.state.currentRate}</td>
                    <td style={{width: "15%"}}>
                        <input type="number"
                            className="form-control"
                            name="hours"
                            value={this.state.inputs.hours}
                            onChange={this.handleHoursChange}/>
                    </td>
                    <td style={{width: "15%"}}>
                        <button 
                            className="btn btn-primary"
                            onClick={this.handleButtonClick}
                            type="button">
                            Insert
                        </button>
                    </td>
                </tr>     
        );
    }
}