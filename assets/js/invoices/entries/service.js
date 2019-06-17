import React, {Component} from 'react';
import SearchableWidget from '../../src/components/searchable_widget';
import axios from 'axios';
import AsyncSelect from '../../src/components/async_select';


class ServiceEntry extends Component{
    state = {
        hours: 0,
        rate: 0,
        fee: 0,
        tax: 0,
        discount: 0,
        selected: ''
    }
    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                hours: 0,
                rate: 0,
                fee: 0,
                discount: 0,
                tax: null,
                selected: ''
            })
            let tax = document.getElementById('product-tax');
            tax.value = 1;
        }

    }

    handler = (evt) =>{
        const name = evt.target.name;
        let newState = {...this.state};
        newState[name] = evt.target.value;
        this.setState(newState, () => this.props.changeHandler(this.state));
    }

    taxHandler = (value) =>{
        axios({
            method: 'get',
            url: '/accounting/api/tax/' + value
        }).then(res =>{
            this.setState({tax: res.data.id + ' - ' 
                                + res.data.name  + '@' 
                                + res.data.rate}, 
                () => this.props.changeHandler(this.state))

        })
    }

    selectHandler = (value) =>{
        const pk = value.split('-')[0];

        axios({
            method: 'get',
            url: '/services/api/service/' + pk
        }).then(res =>{
            this.setState({
                selected: value,
                rate: res.data.hourly_rate,
                fee: res.data.flat_fee
            }, () => this.props.changeHandler(this.state))
        })
        
    }

    clearHandler = () =>{
        this.setState({
            rate: 0,
            hours: 0,
            fee: 0,
            selected: ""
        }, () => this.props.changeHandler(this.state));
        
    }

    insertHandler = () =>{
        //used to reset the tax field
        let taxSelectInput = document.getElementById('service-tax')
        taxSelectInput.value = "";
        this.props.insertHandler()
    }


    render(){
    
        const headStyle = {
            padding: '10px',
            backgroundColor: '#0099ff'
        }
        return(
            <div>
                <table style={{width:"100%"}}>
                    <thead>
                        <tr>
                            <th style={{width:'25%'}}>Service</th>
                            <th style={{width: '10%'}}>Flat Fee</th>
                            <th style={{width: '10%'}}>Hourly Rate</th>
                            <th style={{width: '10%'}}>Hours</th>
                            <th style={{width: '15%'}}>Discount</th>
                            <th style={{width: '15%'}}>Tax</th>
                            <th style={{width: '15%'}}></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td >
                                <SearchableWidget
                                    widgetID="service-widget"
                                    list={this.props.itemList}
                                    dataURL="/services/api/service/"
                                    displayField="name"
                                    idField="id"
                                    canCreateNewItem={true}
                                    newLink='/services/create-service'
                                    model="service"
                                    app="services"
                                    onSelect={this.selectHandler}
                                    onClear={this.clearHandler} />
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    name="fee"
                                    value={this.state.fee}
                                    onChange={this.handler}/>
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    name="rate"
                                    value={this.state.rate}
                                    onChange={this.handler}/>
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    name="hours"
                                    value={this.state.hours}
                                    onChange={this.handler}/>
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    name="discount"
                                    value={this.state.discount}
                                    onChange={this.handler}/>
                            </td>
                            <td>
                                {/*Use a tax choice field */}
                                <AsyncSelect 
                                    noCSS
                                    ID='service-tax'
                                    dataURL="/accounting/api/tax"
                                    name="tax"
                                    resProcessor={(res) =>{
                                        return res.data.map((tax) =>({
                                            name: tax.name,
                                            value: tax.id
                                        }))
                                    }}
                                    handler={this.taxHandler}/>
                            </td>
                            <td>
                                <button 
                                    onClick={this.insertHandler} 
                                    className="invoice-btn" >Insert</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
    };
}

export default ServiceEntry;