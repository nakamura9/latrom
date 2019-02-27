import React, {Component} from 'react';
import SearchableWidget from '../../src/components/searchable_widget';

const inlineStyles = {
    display: "inline",
    float: "left"
};

class ServiceEntry extends Component{
    state = {
        hours: 0
    }
    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                hours: 0
            })
            //remove selected choice from list of choices 
        }
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                hours: 0
            })
            //remove selected choice from list of choices 
        }
    }

    handler = (evt) =>{
        this.setState({hours: evt.target.value})
        this.props.onChangeHours(evt);
    }


    render(){
        
        return(
            <div>
                <table style={{width:"100%"}}>
                    <thead>
                        <tr>
                            <th>Service</th>
                            <th>Hours</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td >
                                <SearchableWidget
                                    list={this.props.itemList}
                                    dataURL="/services/api/service/"
                                    displayField="name"
                                    idField="id"
                                    canCreateNewItem={true}
                                    newLink='/services/create-service'
                                    onSelect={this.props.onSelect}
                                    onClear={this.props.onClear} />
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    placeholder="Hours..."
                                    className="form-control"
                                    value={this.state.hours}
                                    onChange={this.handler}/>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
    };
}
    

class ProductEntry extends Component{
    state = {
        quantity: 0
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                quantity: 0
            })
            //remove selected choice from list of choices 
        }
    }

    handler = (evt) =>{
        if(evt.target.value && evt.target.value > 0){
            this.setState({quantity: evt.target.value})
            this.props.onChangeQuantity(evt);
        }else{
            alert("Please select a valid value greater than 0");
        }
        
    }

    render(){
        return(
            <div>
                <table style={{width:"100%"}}>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <SearchableWidget
                                    list={this.props.itemList}
                                    dataURL="/inventory/api/product/"
                                    displayField="name"
                                    idField="id"
                                    canCreateNewItem={true}
                                    newLink='/inventory/product-create/'
                                    onSelect={this.props.onSelect}
                                    onClear={this.props.onClear} />
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    value={this.state.quantity}
                                    placeholder="Quantity..."
                                    className="form-control"
                                    onChange={this.handler}/>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            )   
    }
}

const BillableEntry = (props) => {
    if(props.billables.length === 0){
            return(
                <div>
                    <center>
                        <h6>The selected customer has no billables</h6>
                        <button 
                        style={{width:"100%"}}
                        className="btn btn-success"
                        onClick={() => window.open(
                            '/accounting/expense/create' ,'popup','width=900,height=480')}>
                        Add Expense <i className="fas fa-plus"></i>
                    </button>
                    </center>
                </div>
            )
        }else{
            return(
                <div style={{width:"100%"}}>
                    <SearchableWidget 
                        dataURL={`/accounting/api/expense/customer/${document.getElementById('id_customer').value}`}
                        onSelect={props.handler}
                        onClear={props.handler}
                        idField="id"
                        displayField="description"
                    />
                    <button 
                        style={{width:"100%"}}
                        className="btn btn-success"
                        onClick={() => window.open(
                            '/accounting/expense/create' ,'popup','width=900,height=480')}>
                        Add Expense <i className="fas fa-plus"></i>
                    </button>
                </div>
            )
        }
};

export {ServiceEntry, BillableEntry, ProductEntry};