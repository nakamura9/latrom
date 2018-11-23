import React, {Component} from 'react';
import {ProductEntry, ServiceEntry, BillableEntry} from './entries'
import axios from 'axios';

class EntryWidget extends Component{
    state = {
        selectedLineType: '',
        billables: [],
        inputs: {

        }
    }

    componentDidMount(){
        document.getElementById('id_customer')
            .addEventListener('change', this.setBillables)
    }

    setBillables = (evt) =>{
        let customerID = evt.target.value;
        axios({
            method: 'GET',
            url: '/invoicing/api/customer/' + customerID
        }).then(res =>{
            this.setState({billables:res.data.expense_set});
        });
    }
    
    handleRadioChange = (evt) => {
        this.setState({selectedLineType: evt.target.value})
    }

    //sale methods 
    handleProductSelect = (value) =>{
        let newInputs = {...this.state.inputs};
        newInputs['item'] = value;
        this.setState({inputs: newInputs});
    }
    handleProductClear = () =>{
        let newInputs = {...this.state.inputs};
        newInputs['item'] = "";
        this.setState({inputs: newInputs});
    }

    handleProductQuantity = (evt) =>{
        let newInputs = {...this.state.inputs};
        newInputs['quantity'] = evt.target.value;
        this.setState({inputs: newInputs});
    }

    //service methods 

    handleServiceSelect = (value) =>{
        let newInputs = {...this.state.inputs};
        newInputs['service'] = value;
        this.setState({inputs: newInputs});
    }
    handleServiceClear = () =>{
        let newInputs = {...this.state.inputs};
        newInputs['service'] = "";
        this.setState({inputs: newInputs});
    }

    handleServiceHours = (evt) =>{
        let newInputs = {...this.state.inputs};
        newInputs['hours'] = evt.target.value;
        this.setState({inputs: newInputs});
    }

    //billables
    handleBillable = (evt) =>{
        let value = evt.target.value;
        let billablesList = this.state.billables.map((billable) =>(
            billable.id + '-' + billable.description
        ))
        if(billablesList.indexOf(value) !== -1){
            this.setState({inputs: {
                    billable: value
                }});
        }
    }

    handleButtonClick = () =>{
        // this is key
        if (this.state.selectedLineType === 'sale'){
            let pk = this.state.inputs['item'].split('-')[0];
            axios({
                url: "/inventory/api/product/" + pk,
                method: "GET"
            }).then( res =>{
                let data = {
                    lineType: 'sale',
                    data: {
                        ...this.state.inputs,
                        price: res.data.unit_sales_price
                    }
                };
                this.props.insertHandler(data);
            });
        }else if(this.state.selectedLineType === 'service'){
            let pk = this.state.inputs['service'].split('-')[0];
            axios({
                url: "/services/api/service/" + pk,
                method: "GET"
            }).then( res =>{
                let data = {
                    lineType: 'service',
                    data: {
                        ...this.state.inputs,
                        rate: res.data.hourly_rate,
                        flatFee: res.data.flat_fee
                    }
                };
                this.props.insertHandler(data);
            });
        }else if(this.state.selectedLineType === 'billable'){
            let pk = this.state.inputs['billable'].split('-')[0];
            axios({
                url: "/accounting/api/expense/" + pk,
                method: "GET"
            }).then( res =>{
                let data = {
                    lineType: 'billable',
                    data: {
                        ...this.state.inputs,
                        description: res.data.description,
                        amount: res.data.amount
                    }
                };
                this.props.insertHandler(data);
            });
        }
            
    }

    render(){
        const theadStyle = {
            padding: '2mm',
            borderRight: '1px solid white',
            color: 'white',
            backgroundColor: '#07f'
        };
        let renderedForm;
        if(this.state.selectedLineType === 'sale'){
            renderedForm = (
                <ProductEntry
                    itemList={this.props.itemList} 
                    onSelect={this.handleProductSelect}
                    onClear={this.handleProductClear}
                    onChangeQuantity={this.handleProductQuantity}
                    />
            );
        }else if(this.state.selectedLineType === 'service'){
            renderedForm = (
                <ServiceEntry 
                    itemList={this.props.itemList}
                    onSelect={this.handleServiceSelect}
                    onClear={this.handleServiceClear}
                    onChangeHours={this.handleServiceHours} />
            );
        }else if(this.state.selectedLineType === "billable"){
            renderedForm = (
                <BillableEntry
                    itemList={this.props.itemList} 
                    billables={this.state.billables}
                    inputHandler={this.handleBillable}/>
            );            
        }else{
            renderedForm = (
                <h6>Choose between a product sale, service or billable expense and enter the appropriate details</h6>
                        
            )
        }
        return(
                <tr style={theadStyle}>
                    <td colSpan={3}>
                        <h3>Invoice Lines</h3>
                        <RadioGroup 
                            handler={this.handleRadioChange} />
                        <hr />
                        
                        <div >
                            <div style={{
                                margin:"10px",
                                padding: "10px"
                            }}>
                                {renderedForm}
                            </div>
                            <br />
                            <button 
                                style={{
                                    display: this.state.selectedLineType === ""
                                        ? "none"
                                        : "block",
                                    clear: "both", 
                                    float:"right"}}
                                className="btn"
                                onClick={this.handleButtonClick}>
                                Insert
                            </button>
                        </div>         
                    </td>
                </tr>
            
        );
    }
}
const RadioGroup = (props) => {
    return(<div >
        <label 
            className="radio-inline" 
            style={{marginLeft: "30px"}}>
            <input 
                type="radio" 
                name="line_type"
                value="sale"
                onChange={props.handler} />Sale
        </label>
        <label 
            className="radio-inline" 
            style={{marginLeft: "30px"}}>
            <input 
                type="radio" 
                name="line_type"
                value="service"
                onChange={props.handler} />Service
        </label>
        <label 
            className="radio-inline" 
            style={{marginLeft: "30px"}}>
            <input 
                type="radio" 
                name="line_type"
                value="billable"
                onChange={props.handler} />Billable
        </label>
    </div>)
}

export default EntryWidget;