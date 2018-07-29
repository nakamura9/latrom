import React, {Component} from 'react';
import $ from 'jquery';

export default class ServiceLineTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            lines: [],
            total: 0.00,
            subtotal: 0.00,
            taxRate: 0.00,
            tax: 0.00,
            total: 0.00
        };    
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
    }
    
    insertLine(data){
        let pk = data['service'].split('-')[0];
        $.ajax({
            url: '/services/api/service/'+ pk,
            method: 'GET'
        }).then(res =>{
            console.log(res);
            let newLines = this.state.lines;
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
                this.updateTotal();
                this.updateForm();
            });
        });
    }

    removeLine(index){
        let newLines = this.state.lines;
        newLines.splice(index, 1);
        this.setState({lines: newLines}, ()=>{
            this.updateTotal();
            this.updateForm();
        });
    }

    updateTotal(){
        console.log('updated');
        let subtotal = this.state.lines.reduce((x, y) => {
            return(x + y.total);
        }, 0);

        let tax = subtotal * (this.state.taxRate /100.0);
        let total = subtotal + tax;
        this.setState({
            subtotal: subtotal,
            tax: tax,
            total: total
        });
    }

    updateForm(){
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
                    <tr key={i}>
                        <td>
                            <button className="btn btn-danger"
                                onClick={() => this.removeLine(i)}>
                                <i className="fas fa-trash"></i>
                            </button>
                        </td>
                        <td>{line.name} + Fixed fee: ${line.fixedFee} </td>
                        <td>{line.rate}</td>
                        <td>{line.hours}</td>
                        <td>{line.total}</td>
                    </tr>
                ))}
                </tbody>
                <tfoot>
                <EntryRow insertLine={this.insertLine.bind(this)}/>
                <tr>
                    <th colSpan={4}>Subtotal</th>
                    <td>{this.state.subtotal.toFixed(2)}</td>
                </tr>
                <tr>
                    <th colSpan={4}>Tax</th>
                    <td>{this.state.tax.toFixed(2)}</td>
                </tr>
                <tr>
                    <th colSpan={4}>Total</th>
                    <td>{this.state.total.toFixed(2)}</td>
                </tr>
            </tfoot>
            </table>
        );
    }
}

class EntryRow extends Component{
    constructor(props){
        super(props);
        this.state = {
            currentRate : 0.00,
            services: [],
            inputs: {
                service: '',
                hours: ''
            }
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

    handleServiceChange(evt){
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

    handleHoursChange(evt){
        let newInputs = this.state.inputs;
        newInputs['hours'] = evt.target.value;
        this.setState({inputs: newInputs});
    }
    handleButtonClick(){
        this.props.insertLine(this.state.inputs)
        this.setState({inputs: {
            service: '',
            hours: ''
        }, 
        currentRate:0.00});
    }
    
    render(){
        return(
                <tr>
                    <td style={{width: "10%"}}></td>
                    <td style={{width: "50%"}}>
                        <input type="text" 
                            list="service-list"
                            className="form-control"
                            name="service" 
                            onChange={this.handleServiceChange.bind(this)}
                            value={this.state.inputs.service}/>
                            <datalist id="service-list">
                                {this.state.services.map((service, i) => {
                                    return(<option key={i}>
                                        {service.id}-{service.name}
                                        </option>)
                                })}
                                
                            </datalist>
                    </td>
                    <td style={{width: "10%"}}>{this.state.currentRate}</td>
                    <td style={{width: "15%"}}>
                        <input type="number"
                            className="form-control"
                            name="hours"
                            value={this.state.inputs.hours}
                            onChange={this.handleHoursChange.bind(this)}/>
                    </td>
                    <td style={{width: "15%"}}>
                        <button className="btn btn-primary"
                                onClick={this.handleButtonClick.bind(this)}
                            >
                            Insert
                        </button>
                    </td>
                </tr>     
        );
    }
}